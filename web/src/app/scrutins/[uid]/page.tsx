import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArrowLeftIcon, ArrowSquareOutIcon } from "@phosphor-icons/react/dist/ssr";
import { LINK_TEXT } from "@/components/button-styles";
import { PositionBar, PositionLegend } from "@/components/position-bar";
import { Flap } from "@/components/flap";
import { ResultBadge } from "@/components/result-badge";
import { Unavailable } from "@/components/unavailable";
import { VotesExplorer } from "@/components/votes-explorer";
import { PHASE_PRODUCTION_BUILD } from "next/constants";
import { CivixError, listScrutins } from "@/lib/civix";
import { getScrutinPage, type ScrutinPageData } from "@/lib/data/scrutin";
import { settle } from "@/lib/data/result";
import { formatLongDay, formatNumber } from "@/lib/format";
import { truncate } from "@/lib/text";

export const revalidate = 21600;
export const dynamicParams = true;

const STATIC_PARAMS_COUNT = 50;

const UID_PATTERN = /^VTANR5L\d{1,2}V\d{1,6}$/;
const DESCRIPTION_LIMIT = 160;

type PageProps = { params: Promise<{ uid: string }> };

export async function generateStaticParams(): Promise<Array<{ uid: string }>> {
  try {
    const page = await listScrutins({ pageSize: STATIC_PARAMS_COUNT });
    return page.scrutins.filter((scrutin) => UID_PATTERN.test(scrutin.uid)).map((scrutin) => ({ uid: scrutin.uid }));
  } catch {
    return [];
  }
}

async function load(uid: string): Promise<{ data: ScrutinPageData } | { missing: true } | { unavailable: true }> {
  try {
    return { data: await getScrutinPage(uid) };
  } catch (error) {
    if (error instanceof CivixError && error.status === 404) {
      return { missing: true };
    }
    if (process.env.NEXT_PHASE === PHASE_PRODUCTION_BUILD) {
      return { unavailable: true };
    }
    throw error;
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
    <Link href="/" className={`${LINK_TEXT} inline-flex items-center gap-2 text-sm font-bold`}>
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
    <div className="flex flex-col gap-1 border-t border-line pt-3">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-base font-medium">{value}</dd>
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
  if ("unavailable" in loaded) {
    return (
      <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-6 px-4 pb-24 pt-12 sm:px-6">
        <BackLink />
        <Unavailable />
      </main>
    );
  }
  const { data } = loaded;
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-14 px-4 pb-24 pt-10 sm:px-6">
      <header className="flex flex-col gap-6">
        <BackLink />
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          {data.numero !== null ? (
            <span className="flex items-center gap-2">
              <span className="font-display text-lg font-semibold">Scrutin n°</span>
              <Flap value={String(data.numero)} label={String(data.numero)} className="text-3xl font-semibold" />
            </span>
          ) : (
            <span className="font-display text-lg font-semibold">Scrutin</span>
          )}
          <span className="text-base text-ink-soft">
            {data.legislature !== null ? `${data.legislature}e législature` : ""}
            {data.legislature !== null && data.date !== null ? ", " : ""}
            {data.date !== null ? formatLongDay(data.date) : ""}
          </span>
        </div>
        <h1 className="max-w-4xl font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">{data.title}</h1>
        {data.dossier !== null ? <p className="max-w-measure text-lg text-ink-soft">Dossier : {data.dossier.label}</p> : null}
        <div className="flex flex-wrap items-center gap-3">
          <ResultBadge result={data.result} />
          {data.resultLabel !== null ? <span className="text-sm text-ink-soft">{data.resultLabel}</span> : null}
        </div>
      </header>

      <section aria-labelledby="resultat-titre" className="flex flex-col gap-5 border-t-2 border-rule pt-4">
        <h2 id="resultat-titre" className="font-display text-3xl font-semibold tracking-tight">
          Résultat
        </h2>
        {data.counts !== null ? (
          <>
            <PositionBar counts={data.counts} label="Résultat du scrutin" size="large" />
            <PositionLegend counts={data.counts} />
            <p className="text-sm text-ink-soft">{formatNumber(data.counts.total)} votants enregistrés.</p>
          </>
        ) : (
          <p className="text-base text-muted">Les décomptes de ce scrutin ne sont pas disponibles.</p>
        )}
        <dl className="mt-2 grid gap-x-8 gap-y-4 sm:grid-cols-2 lg:grid-cols-4">
          <Fact label="Type de vote" value={data.voteType} />
          <Fact label="Règle de majorité" value={data.majorityRule} />
          <Fact label="Mode de vote" value={data.voteMode} />
          <Fact label="Demandé par" value={data.requestedBy} />
        </dl>
      </section>

      <section aria-labelledby="groupes-titre" className="flex flex-col gap-5 border-t-2 border-rule pt-4">
        <h2 id="groupes-titre" className="font-display text-3xl font-semibold tracking-tight">
          Détail par groupe
        </h2>
        {data.byGroup.length === 0 ? (
          <p className="text-base text-muted">Le détail par groupe n'est pas disponible pour ce scrutin.</p>
        ) : (
          <ul className="flex flex-col">
            {data.byGroup.map((group) => (
              <li
                key={`${group.abbr}-${group.label}`}
                className="flex flex-col gap-2 border-b border-line py-4 lg:grid lg:grid-cols-[minmax(0,4fr)_minmax(0,8fr)] lg:items-center lg:gap-x-8"
              >
                <p className="text-base">
                  {group.abbr !== null ? <span className="font-display text-lg font-semibold">{group.abbr} </span> : null}
                  <span className="text-ink-soft">{group.label}</span>
                </p>
                <div className="flex flex-col gap-2">
                  <PositionBar counts={group.counts} label={group.label} />
                  <PositionLegend counts={group.counts} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="declarations-titre" className="flex flex-col gap-5 border-t-2 border-rule pt-4">
        <h2 id="declarations-titre" className="font-display text-3xl font-semibold tracking-tight">
          Déclarations des groupes
        </h2>
        {!data.statementsAvailable ? (
          <p className="text-base text-muted">Les déclarations ne peuvent pas être chargées pour le moment.</p>
        ) : data.statements.length === 0 ? (
          <p className="max-w-measure text-base text-ink-soft">
            Aucun groupe n'a publié d'explication de vote pour ce scrutin. C'est fréquent.
          </p>
        ) : (
          <ul className="grid gap-x-10 md:grid-cols-2">
            {data.statements.map((statement) => (
              <li key={`${statement.abbr}-${statement.text.slice(0, 24)}`} className="flex flex-col gap-2 border-b border-line py-4">
                <p className="font-display text-lg font-semibold">
                  {statement.abbr ?? statement.label}
                  {statement.position !== null ? <span className="font-normal text-muted">, {statement.position}</span> : null}
                </p>
                <p className="text-base">{statement.text}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="votes-titre" className="flex flex-col gap-5 border-t-2 border-rule pt-4">
        <h2 id="votes-titre" className="font-display text-3xl font-semibold tracking-tight">
          Votes de chaque député
        </h2>
        {data.votes.length === 0 ? (
          <p className="text-base text-muted">La liste des votes individuels n'est pas disponible pour ce scrutin.</p>
        ) : (
          <VotesExplorer votes={data.votes} groupOptions={data.groupOptions} />
        )}
      </section>

      <section aria-labelledby="sources-titre" className="flex flex-col gap-4 border-t-2 border-rule pt-4">
        <h2 id="sources-titre" className="font-display text-3xl font-semibold tracking-tight">
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
