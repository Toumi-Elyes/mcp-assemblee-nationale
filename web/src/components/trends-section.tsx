import Link from "next/link";
import { formatNumber, formatPercent, formatShortDay, pluralize } from "@/lib/format";
import type { Counts, Scrutin } from "@/lib/civix/types";
import type { Coverage, KindStat, VoteKind, VotesPerDay } from "@/lib/stats";
import { truncate } from "@/lib/text";
import { CountsText } from "./position-bar";
import { ResultBadge } from "./result-badge";
import { Section, Unavailable } from "./section";
import { TopDossiers, type TopDossierPeriod } from "./top-dossiers";
import { VotesPerDayChart } from "./votes-per-day-chart";

const KIND_LABELS: Record<VoteKind, string> = {
  ensemble: "Votes sur l'ensemble d'un texte",
  texte: "Autres votes sur un texte (motions…)",
  article: "Articles",
  amendement: "Amendements",
  autre: "Autres scrutins (résolutions…)",
};

const FINAL_TITLE_LIMIT = 150;

export type TrendsData = {
  perDay: VotesPerDay;
  periods: TopDossierPeriod[];
  kinds: KindStat[];
  kindsCoverage: Coverage;
  finalVotes: Scrutin[] | null;
  finalCounts: Map<string, Counts>;
};

const Card: React.FC<{ title: string; children: React.ReactNode; className?: string }> = ({
  title,
  children,
  className,
}) => {
  return (
    <div className={`card p-5 ${className ?? ""}`}>
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      {children}
    </div>
  );
};

const AdoptionByKind: React.FC<{ kinds: KindStat[]; coverage: Coverage }> = ({ kinds, coverage }) => {
  return (
    <div>
      <p className="mb-3 text-sm text-muted">
        Part des scrutins adoptés, du {formatShortDay(coverage.from)} au {formatShortDay(coverage.to)}.
      </p>
      <ul className="space-y-3">
        {kinds.map((stat) => (
          <li key={stat.kind}>
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-sm font-medium">{KIND_LABELS[stat.kind]}</span>
              <span className="whitespace-nowrap text-sm tabular-nums text-muted">
                {stat.adoptionRate !== null ? formatPercent(stat.adoptionRate) : "—"} adoptés
              </span>
            </div>
            <div
              role="img"
              aria-label={`${stat.adopted} adoptés sur ${stat.total} scrutins`}
              className="mt-1 h-2 overflow-hidden rounded-full bg-surface-2"
            >
              <div
                className="h-full rounded-full"
                style={{ width: `${(stat.adoptionRate ?? 0) * 100}%`, background: "var(--bar)" }}
              />
            </div>
            <p className="mt-0.5 text-xs text-muted">
              {formatNumber(stat.adopted)} sur {pluralize(stat.total, "scrutin")}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

const FinalVotes: React.FC<{ votes: Scrutin[]; counts: Map<string, Counts> }> = ({ votes, counts }) => {
  return (
    <ul className="divide-y divide-line">
      {votes.map((scrutin) => {
        const scrutinCounts = counts.get(scrutin.uid);
        return (
          <li key={scrutin.uid} className="py-3 first:pt-0 last:pb-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              {scrutin.date !== null ? (
                <time dateTime={scrutin.date} className="text-xs text-muted">
                  {formatShortDay(scrutin.date)}
                </time>
              ) : null}
              <ResultBadge result={scrutin.result} />
            </div>
            <Link href={`/scrutins/${scrutin.uid}`} className="mt-1 block text-sm font-medium hover:underline">
              {truncate(scrutin.title, FINAL_TITLE_LIMIT)}
            </Link>
            {scrutinCounts ? (
              <p className="mt-0.5 text-xs text-muted">
                <CountsText counts={scrutinCounts} />
              </p>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
};

export const TrendsSection: React.FC<{ trends: TrendsData | null }> = ({ trends }) => {
  return (
    <Section
      id="tendances"
      eyebrow="Tendances"
      title="Ce que montrent les votes récents"
      intro="Calculé à partir des scrutins publiés. Ces chiffres décrivent l'activité de l'Assemblée, sans jugement."
    >
      {trends === null ? (
        <Unavailable />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card title="Scrutins par jour" className="lg:col-span-2">
            <VotesPerDayChart data={trends.perDay} />
          </Card>
          <Card title="Textes les plus votés">
            <TopDossiers periods={trends.periods} />
          </Card>
          <Card title="Adoption selon le type de vote">
            <AdoptionByKind kinds={trends.kinds} coverage={trends.kindsCoverage} />
          </Card>
          <Card title="Derniers votes sur l'ensemble d'un texte" className="lg:col-span-2">
            {trends.finalVotes === null || trends.finalVotes.length === 0 ? (
              <Unavailable />
            ) : (
              <FinalVotes votes={trends.finalVotes} counts={trends.finalCounts} />
            )}
          </Card>
        </div>
      )}
    </Section>
  );
};
