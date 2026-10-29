import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArrowLeftIcon, ArrowSquareOutIcon } from "@phosphor-icons/react/dist/ssr";
import { LINK_TEXT } from "@/components/button-styles";
import { PositionBar, PositionLegend } from "@/components/position-bar";
import { ResultBadge } from "@/components/result-badge";
import { Unavailable } from "@/components/unavailable";
import { VotesExplorer } from "@/components/votes-explorer";
import { CivixError } from "@/lib/civix";
import { getScrutinPage, type ScrutinPageData } from "@/lib/data/scrutin";
import { settle } from "@/lib/data/result";
import { formatLongDay, formatNumber } from "@/lib/format";
import { truncate } from "@/lib/text";

export const revalidate = 21600;

const UID_PATTERN = /^[A-Za-z0-9_-]{3,64}$/;
const DESCRIPTION_LIMIT = 160;

type PageProps = { params: Promise<{ uid: string }> };

async function load(uid: string): Promise<{ data: ScrutinPageData } | { missing: true } | { error: true }> {
  try {
    return { data: await getScrutinPage(uid) };
  } catch (error) {
    if (error instanceof CivixError && error.status === 404) {
      return { missing: true };
    }
    return { error: true };
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { uid } = await params;
  if (!UID_PATTERN.test(uid)) {
    return { title: "Scrutin introuvable" };
  }
  const loaded = await settle(load(uid));
  if (!loaded.ok || !("data" in loaded.data)) {
    return { title: "Détail d'un scrutin" };
  }
  const { data } = loaded.data;
  return {
    title: truncate(data.title, 70),
    description: truncate(
      `Scrutin ${data.numero ?? ""} de l'Assemblée nationale${data.date !== null ? ` du ${formatLongDay(data.date)}` : ""} : ${data.title}`,
      DESCRIPTION_LIMIT,
    ),
    alternates: { canonical: `/scrutins/${uid}` },
  };
}

const BackLink: React.FC = () => {
  return (
    <Link href="/" className={`${LINK_TEXT} inline-flex items-center gap-2 text-sm font-semibold`}>
      <ArrowLeftIcon aria-hidden="true" size={16} weight="bold" />
      Retour à l'accueil
    </Link>
  );
};

const Fact: React.FC<{ label: string; value: string | null }> = ({ label, value }) => {
  if (value === null || value === "") {
    return null;
  }
  return (
    <div className="flex flex-col gap-1">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="text-sm font-medium">{value}</dd>
    </div>
  );
};

const ScrutinPage = async ({ params }: PageProps) => {
  const { uid } = await params;
  if (!UID_PATTERN.test(uid)) {
    notFound();
  }
  const loaded = await load(uid);
  if ("missing" in loaded) {
    notFound();
  }
  if ("error" in loaded) {
    return (
      <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-6 px-4 pb-24 pt-24 sm:px-6">
        <BackLink />
        <Unavailable />
      </main>
    );
  }
  const { data } = loaded;
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-12 px-4 pb-24 pt-24 sm:px-6">
      <header className="flex flex-col gap-4">
        <BackLink />
        <p className="text-sm text-muted">
          {data.numero !== null ? `Scrutin n° ${data.numero}` : "Scrutin"}
          {data.legislature !== null ? `, ${data.legislature}e législature` : ""}
          {data.date !== null ? `, ${formatLongDay(data.date)}` : ""}
        </p>
        <h1 className="max-w-hero text-4xl font-semibold tracking-tight">{data.title}</h1>
        {data.dossier !== null ? <p className="max-w-hero text-lg text-muted">Dossier : {data.dossier.label}</p> : null}
        <div className="flex flex-wrap items-center gap-3">
          <ResultBadge result={data.result} />
          {data.resultLabel !== null ? <span className="text-sm text-muted">{data.resultLabel}</span> : null}
        </div>
      </header>

      <section aria-labelledby="resultat-titre" className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-6">
        <h2 id="resultat-titre" className="text-2xl font-semibold">
          Résultat
        </h2>
        {data.counts !== null ? (
          <>
            <PositionBar counts={data.counts} label="Résultat du scrutin" />
            <PositionLegend counts={data.counts} />
            <p className="text-sm text-muted">{formatNumber(data.counts.total)} votants enregistrés.</p>
          </>
        ) : (
          <p className="text-base text-muted">Les décomptes de ce scrutin ne sont pas disponibles.</p>
        )}
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Fact label="Type de vote" value={data.voteType} />
          <Fact label="Règle de majorité" value={data.majorityRule} />
          <Fact label="Mode de vote" value={data.voteMode} />
          <Fact label="Demandé par" value={data.requestedBy} />
        </dl>
      </section>

      <section aria-labelledby="groupes-titre" className="flex flex-col gap-4">
        <h2 id="groupes-titre" className="text-2xl font-semibold">
          Détail par groupe
        </h2>
        {data.byGroup.length === 0 ? (
          <p className="text-base text-muted">Le détail par groupe n'est pas disponible pour ce scrutin.</p>
        ) : (
          <ul className="grid gap-3 md:grid-cols-2">
            {data.byGroup.map((group) => (
              <li key={`${group.abbr}-${group.label}`} className="flex flex-col gap-3 rounded-2xl border border-line bg-raised p-6">
                <p className="text-base font-semibold">
                  {group.abbr !== null ? `${group.abbr} ` : ""}
                  <span className="font-normal text-muted">{group.label}</span>
                </p>
                <PositionBar counts={group.counts} label={group.label} />
                <PositionLegend counts={group.counts} />
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="declarations-titre" className="flex flex-col gap-4">
        <h2 id="declarations-titre" className="text-2xl font-semibold">
          Déclarations des groupes
        </h2>
        {!data.statementsAvailable ? (
          <p className="text-base text-muted">Les déclarations ne peuvent pas être chargées pour le moment.</p>
        ) : data.statements.length === 0 ? (
          <p className="max-w-hero text-base text-muted">
            Aucun groupe n'a publié d'explication de vote pour ce scrutin. C'est fréquent.
          </p>
        ) : (
          <ul className="grid gap-3 md:grid-cols-2">
            {data.statements.map((statement) => (
              <li key={`${statement.abbr}-${statement.text.slice(0, 24)}`} className="flex flex-col gap-2 rounded-2xl border border-line bg-raised p-6">
                <p className="text-base font-semibold">
                  {statement.abbr ?? statement.label}
                  {statement.position !== null ? <span className="font-normal text-muted">, {statement.position}</span> : null}
                </p>
                <p className="text-base">{statement.text}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="votes-titre" className="flex flex-col gap-4">
        <h2 id="votes-titre" className="text-2xl font-semibold">
          Votes de chaque député
        </h2>
        {data.votes.length === 0 ? (
          <p className="text-base text-muted">La liste des votes individuels n'est pas disponible pour ce scrutin.</p>
        ) : (
          <VotesExplorer votes={data.votes} groupOptions={data.groupOptions} />
        )}
      </section>

      <section aria-labelledby="sources-titre" className="flex flex-col gap-3">
        <h2 id="sources-titre" className="text-2xl font-semibold">
          Sources
        </h2>
        <ul className="flex flex-col gap-2 text-base">
          {data.assembleeUrl !== null ? (
            <li>
              <a href={data.assembleeUrl} className={`${LINK_TEXT} inline-flex items-center gap-1`}>
                Page du scrutin sur assemblee-nationale.fr <ArrowSquareOutIcon aria-hidden="true" size={16} />
              </a>
            </li>
          ) : null}
          <li>
            <a href={data.civixUrl} className={`${LINK_TEXT} inline-flex items-center gap-1`}>
              Page du scrutin sur CIVIX <ArrowSquareOutIcon aria-hidden="true" size={16} />
            </a>
          </li>
        </ul>
      </section>
    </main>
  );
};

export default ScrutinPage;
