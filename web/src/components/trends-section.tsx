import { formatPercent, formatShortDay } from "@/lib/format";
import type { VoteKind } from "@/lib/stats";
import type { TrendsData } from "@/lib/data/view-types";
import { Reveal } from "./reveal";
import { ScrutinRow } from "./scrutin-row";
import { TopDossiers } from "./top-dossiers";
import { VotesPerDayChart } from "./votes-per-day-chart";

const KIND_LABELS: Record<VoteKind, string> = {
  ensemble: "Vote sur l'ensemble d'un texte",
  texte: "Texte",
  article: "Article",
  amendement: "Amendement",
  autre: "Autre",
};

const Card: React.FC<{ title: string; note?: string; children: React.ReactNode }> = ({ title, note, children }) => {
  return (
    <Reveal className="h-full">
      <article className="flex h-full flex-col gap-4 rounded-2xl border border-line bg-raised p-6">
        <header className="flex flex-col gap-1">
          <h4 className="text-lg font-semibold">{title}</h4>
          {note !== undefined ? <p className="text-sm text-muted">{note}</p> : null}
        </header>
        {children}
      </article>
    </Reveal>
  );
};

export const TrendsSection: React.FC<{ trends: TrendsData }> = ({ trends }) => {
  const { perDay, kinds, kindsCoverage, finalVotes, finalCounts } = trends;
  const partial = !perDay.coverage.complete;
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-2xl font-semibold">Tendances</h3>
        <p className="max-w-hero text-base text-muted">
          Calculées sur les scrutins lus en direct.
          {partial ? ` Fenêtre partielle, à partir du ${formatShortDay(perDay.coverage.from)}.` : ""}
        </p>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Scrutins par jour" note={`${perDay.total} scrutins sur la période.`}>
          <VotesPerDayChart data={perDay} />
        </Card>
        <Card title="Dossiers les plus votés" note="Nombre de scrutins par dossier législatif.">
          <TopDossiers periods={trends.periods} />
        </Card>
        <Card
          title="Taux d'adoption par type de vote"
          note={`Du ${formatShortDay(kindsCoverage.from)} au ${formatShortDay(kindsCoverage.to)}.`}
        >
          {kinds.length === 0 ? (
            <p className="text-sm text-muted">Pas assez de scrutins sur la période.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {kinds.map((kind) => (
                <li key={kind.kind} className="flex flex-col gap-1">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="text-sm font-medium">{KIND_LABELS[kind.kind]}</span>
                    <span className="tabular font-mono text-sm">
                      {kind.adoptionRate !== null ? formatPercent(kind.adoptionRate) : "n/d"}
                    </span>
                  </div>
                  <svg
                    role="img"
                    aria-label={`${kind.adopted} adoptés sur ${kind.total}`}
                    className="h-2 w-full overflow-hidden rounded-sm"
                    preserveAspectRatio="none"
                  >
                    <rect width="100%" height="100%" className="fill-absent" />
                    <rect width={`${(kind.adoptionRate ?? 0) * 100}%`} height="100%" className="fill-accent" />
                  </svg>
                  <span className="text-xs text-muted">
                    {kind.total} votes : {kind.adopted} adoptés, {kind.rejected} rejetés
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card title="Derniers votes sur l'ensemble d'un texte" note="Les votes finals, du plus récent au plus ancien.">
          {finalVotes === null || finalVotes.length === 0 ? (
            <p className="text-sm text-muted">Aucun vote sur l'ensemble d'un texte à afficher pour le moment.</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {finalVotes.map((scrutin) => (
                <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={finalCounts.get(scrutin.uid)} />
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
};
