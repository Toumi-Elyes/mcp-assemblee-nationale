import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { PositionBar, PositionLegend } from "@/components/position-bar";
import { ResultBadge } from "@/components/result-badge";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Unavailable } from "@/components/section";
import { VotesExplorer } from "@/components/votes-explorer";
import { CivixError } from "@/lib/civix";
import { getScrutinPage, type ScrutinPageData } from "@/lib/data/scrutin";
import { type Loaded } from "@/lib/data/result";
import { POSITION_LABELS, formatLongDay, formatNumber } from "@/lib/format";
import { truncate } from "@/lib/text";

export const revalidate = 3600;

export function generateStaticParams() {
  return [];
}

const UID_PATTERN = /^[A-Za-z0-9_-]{3,64}$/;
const META_TITLE_LIMIT = 90;
const META_DESCRIPTION_LIMIT = 200;

type PageProps = { params: Promise<{ uid: string }> };

async function load(uid: string): Promise<Loaded<ScrutinPageData>> {
  if (!UID_PATTERN.test(uid)) {
    notFound();
  }
  try {
    return { ok: true, data: await getScrutinPage(uid) };
  } catch (error) {
    if (error instanceof CivixError && error.status === 404) {
      notFound();
    }
    return { ok: false };
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { uid } = await params;
  const result = await load(uid);
  if (!result.ok) {
    return { title: "Scrutin", robots: { index: false } };
  }
  const { data } = result;
  const counts = data.counts;
  const description = [
    data.dossier?.label ?? null,
    formatLongDay(data.date),
    data.resultLabel,
    counts
      ? `${counts.pour} pour, ${counts.contre} contre, ${counts.abstention} abstentions`
      : null,
  ]
    .filter((part): part is string => part !== null)
    .join(" · ");
  return {
    title: truncate(data.title, META_TITLE_LIMIT),
    description: truncate(description, META_DESCRIPTION_LIMIT),
    alternates: { canonical: `/scrutins/${data.uid}` },
  };
}

const Stat: React.FC<{ label: string; value: number; color: string }> = ({ label, value, color }) => {
  return (
    <div className="card p-4">
      <dt className="flex items-center gap-2 text-sm text-muted">
        <span aria-hidden className="size-2.5 rounded-sm" style={{ background: color }} />
        {label}
      </dt>
      <dd className="font-serif text-3xl font-semibold tabular-nums">{formatNumber(value)}</dd>
    </div>
  );
};

const ScrutinPage = async ({ params }: PageProps) => {
  const { uid } = await params;
  const result = await load(uid);

  return (
    <>
      <SiteHeader />
      <main id="contenu" className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
        <Link href="/#semaine" className="link inline-flex items-center gap-1 text-sm">
          <ArrowLeft aria-hidden className="size-4" />
          Retour à l&apos;accueil
        </Link>
        {result.ok ? <Details data={result.data} /> : <div className="mt-8"><Unavailable /></div>}
      </main>
      <SiteFooter updatedAt={new Date()} />
    </>
  );
};

const Details: React.FC<{ data: ScrutinPageData }> = ({ data }) => {
  const { counts } = data;
  const facts = [
    data.voteType,
    data.voteMode,
    data.majorityRule,
    data.requestedBy !== null ? `Demandé par : ${data.requestedBy}` : null,
  ].filter((fact): fact is string => fact !== null);

  return (
    <>
      <header className="mt-6">
        {data.dossier !== null ? <p className="eyebrow mb-2">{data.dossier.label}</p> : null}
        <h1 className="text-3xl font-semibold leading-tight sm:text-4xl">{data.title}</h1>
        <p className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-muted">
          {data.date !== null ? <time dateTime={data.date}>{formatLongDay(data.date)}</time> : null}
          {data.numero !== null ? <span>Scrutin n° {data.numero}</span> : null}
          {data.legislature !== null ? <span>{data.legislature}e législature</span> : null}
          <ResultBadge result={data.result} />
        </p>
        {data.resultLabel !== null ? (
          <p className="mt-2 text-sm text-muted">Résultat officiel : {data.resultLabel}.</p>
        ) : null}
      </header>

      {counts ? (
        <section aria-labelledby="decompte" className="mt-8">
          <h2 id="decompte" className="mb-3 text-xl font-semibold">
            Décompte
          </h2>
          <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Stat label={POSITION_LABELS.pour} value={counts.pour} color="var(--pos-pour)" />
            <Stat label={POSITION_LABELS.contre} value={counts.contre} color="var(--pos-contre)" />
            <Stat label="Abstentions" value={counts.abstention} color="var(--pos-abstention)" />
            <Stat label="Non-votants" value={counts.non_votant} color="var(--pos-non-votant)" />
          </dl>
          <PositionBar counts={counts} className="mt-4" height="h-4" />
          <p className="mt-2 text-sm text-muted">{formatNumber(counts.total)} députés concernés.</p>
        </section>
      ) : null}

      {facts.length > 0 ? (
        <ul className="mt-4 flex flex-wrap gap-2 text-xs text-muted">
          {facts.map((fact) => (
            <li key={fact} className="rounded-full border border-line px-2.5 py-1">
              {fact}
            </li>
          ))}
        </ul>
      ) : null}

      {data.byGroup.length > 0 ? (
        <section aria-labelledby="par-groupe" className="mt-10">
          <h2 id="par-groupe" className="text-xl font-semibold">
            Répartition par groupe
          </h2>
          <p className="mt-1 text-sm text-muted">Positions des députés de chaque groupe au moment du vote.</p>
          <div className="mt-3">
            <PositionLegend />
          </div>
          <ul className="card mt-4 divide-y divide-line">
            {[...data.byGroup]
              .sort((a, b) => b.counts.total - a.counts.total || (a.abbr ?? "").localeCompare(b.abbr ?? ""))
              .map((row) => (
                <li key={`${row.abbr ?? row.label}-${row.counts.total}`} className="p-4">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <span>
                      <span className="font-semibold">{row.abbr ?? "Groupe"}</span>{" "}
                      <span className="text-sm text-muted">{row.label}</span>
                    </span>
                    <span className="text-sm tabular-nums text-muted">
                      {formatNumber(row.counts.pour)} pour · {formatNumber(row.counts.contre)} contre ·{" "}
                      {formatNumber(row.counts.abstention)} abst. · {formatNumber(row.counts.non_votant)} non-vot.
                    </span>
                  </div>
                  <PositionBar counts={row.counts} className="mt-2" />
                </li>
              ))}
          </ul>
        </section>
      ) : null}

      {data.statements.length > 0 ? (
        <section aria-labelledby="declarations" className="mt-10">
          <h2 id="declarations" className="text-xl font-semibold">
            Déclarations des groupes
          </h2>
          <p className="mt-1 text-sm text-muted">Textes publiés par les groupes, reproduits tels quels.</p>
          <ul className="mt-4 space-y-3">
            {data.statements.map((statement) => (
              <li key={`${statement.abbr ?? statement.label}-${statement.text.slice(0, 20)}`} className="card p-4">
                <p className="font-semibold">
                  {statement.abbr ?? statement.label}
                  {statement.position !== null ? (
                    <span className="font-normal text-muted"> · vote : {statement.position}</span>
                  ) : null}
                </p>
                <blockquote className="mt-1 text-sm">{statement.text}</blockquote>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {data.votes.length > 0 ? (
        <section aria-labelledby="votes" className="mt-10">
          <h2 id="votes" className="mb-3 text-xl font-semibold">
            Vote de chaque député
          </h2>
          <VotesExplorer votes={data.votes} groupOptions={data.groupOptions} />
        </section>
      ) : null}

      <section aria-labelledby="sources" className="mt-10 card p-5">
        <h2 id="sources" className="text-lg font-semibold">
          Sources
        </h2>
        <ul className="mt-2 space-y-1 text-sm">
          <li>
            <a className="link inline-flex items-center gap-1" href={data.civixUrl} target="_blank" rel="noreferrer">
              Page du scrutin sur CIVIX <ExternalLink aria-hidden className="size-3" />
            </a>
          </li>
          {data.assembleeUrl !== null ? (
            <li>
              <a className="link inline-flex items-center gap-1" href={data.assembleeUrl} target="_blank" rel="noreferrer">
                Scrutin sur le site de l&apos;Assemblée nationale <ExternalLink aria-hidden className="size-3" />
              </a>
            </li>
          ) : null}
        </ul>
        <p className="mt-3 text-xs text-muted">
          Données publiques de l&apos;Assemblée nationale, présentées par CIVIX (initiative indépendante).
        </p>
      </section>
    </>
  );
};

export default ScrutinPage;
