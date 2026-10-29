import { endSentence, formatPercent, formatShortDay, pluralize } from "@/lib/format";
import type { VoteKind } from "@/lib/stats";
import type { TrendsData } from "@/lib/data/view-types";
import { Plate } from "./plate";
import { BoardHead, ScrutinRow } from "./scrutin-row";
import { TopDossiers } from "./top-dossiers";
import { VotesPerDayChart } from "./votes-per-day-chart";

const KIND_LABELS: Record<VoteKind, string> = {
  ensemble: "Vote sur l'ensemble d'un texte",
  texte: "Texte",
  article: "Article",
  amendement: "Amendement",
  autre: "Autre",
};

export const TrendsSection: React.FC<{ trends: TrendsData }> = ({ trends }) => {
  const { perDay, kinds, kindsCoverage, finalVotes, finalCounts } = trends;
  const partial = !perDay.coverage.complete;
  return (
    <div className="flex flex-col gap-6">
      {partial ? (
        <p className="max-w-measure text-base text-ink-soft">
          Période partielle : à partir du {formatShortDay(perDay.coverage.from)}.
        </p>
      ) : null}
      <div className="grid gap-x-12 gap-y-14 lg:grid-cols-12">
        <Plate number={1} title="Scrutins par jour" note={`${perDay.total} scrutins sur la période.`} className="lg:col-span-7">
          <VotesPerDayChart data={perDay} />
        </Plate>
        <Plate
          number={2}
          title="Dossiers les plus votés"
          note="Nombre de scrutins par dossier législatif."
          className="lg:col-span-5"
        >
          <TopDossiers periods={trends.periods} />
        </Plate>
        <Plate
          number={3}
          title="Taux d'adoption par type de vote"
          note={endSentence(`Du ${formatShortDay(kindsCoverage.from)} au ${formatShortDay(kindsCoverage.to)}`)}
          className="lg:col-span-4"
        >
          {kinds.length === 0 ? (
            <p className="text-sm text-muted">Pas assez de scrutins sur la période.</p>
          ) : (
            <ul className="flex flex-col gap-4">
              {kinds.map((kind) => (
                <li key={kind.kind} className="flex flex-col gap-1.5">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="text-sm font-medium">{KIND_LABELS[kind.kind]}</span>
                    <span className="tabular font-display text-lg font-semibold">
                      {kind.adoptionRate !== null ? formatPercent(kind.adoptionRate) : "n/d"}
                    </span>
                  </div>
                  <svg
                    role="img"
                    aria-label={`${kind.adopted} adoptés sur ${kind.total}`}
                    className="h-2.5 w-full"
                    preserveAspectRatio="none"
                  >
                    <rect width="100%" height="100%" className="fill-absent" />
                    <rect width={`${(kind.adoptionRate ?? 0) * 100}%`} height="100%" className="fill-ink" />
                  </svg>
                  <span className="text-xs text-muted">
                    {pluralize(kind.total, "vote")} : {pluralize(kind.adopted, "adopté")}, {pluralize(kind.rejected, "rejeté")}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Plate>
        <Plate
          number={4}
          title="Derniers votes sur l'ensemble d'un texte"
          note="Les votes finals, du plus récent au plus ancien."
          className="lg:col-span-8"
        >
          {finalVotes === null || finalVotes.length === 0 ? (
            <p className="text-sm text-muted">Aucun vote sur l'ensemble d'un texte à afficher pour le moment.</p>
          ) : (
            <div className="flex flex-col">
              <BoardHead />
              <ul className="flex flex-col">
                {finalVotes.map((scrutin) => (
                  <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={finalCounts.get(scrutin.uid)} />
                ))}
              </ul>
            </div>
          )}
        </Plate>
      </div>
    </div>
  );
};
