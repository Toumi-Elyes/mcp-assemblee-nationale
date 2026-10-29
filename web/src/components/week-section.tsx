"use client";

import { formatShortDay, pluralize } from "@/lib/format";
import { Flap } from "./flap";
import { useLive } from "./live-context";
import { LiveStatus } from "./live-status";
import { BoardHead, ScrutinRow } from "./scrutin-row";
import { Unavailable } from "./unavailable";

export const WeekSection: React.FC = () => {
  const { snapshot } = useLive();
  const { week } = snapshot;
  return (
    <section aria-labelledby="semaine-titre" className="flex flex-col gap-2">
      <header className="flex flex-col gap-1.5 border-b-2 border-rule pb-3">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
          <h2 id="semaine-titre" className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            Cette semaine à l'Assemblée
          </h2>
          {week !== null ? (
            <span className="flex items-center gap-2">
              <Flap value={String(week.total)} label={`${week.total} scrutins`} className="text-3xl font-semibold" />
              <span className="font-display text-lg font-semibold">scrutins</span>
            </span>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-ink-soft">
          {week !== null ? (
            <p>
              Du {formatShortDay(week.from)} au {formatShortDay(week.to)}, regroupés par dossier.
            </p>
          ) : null}
          <LiveStatus />
        </div>
      </header>
      {week === null ? (
        <Unavailable />
      ) : (
        <div className="flex flex-col gap-4">
          <BoardHead />
          {week.groups.map((group) => (
            <section key={group.key} aria-label={group.label ?? "Scrutins sans dossier rattaché"} className="flex flex-col">
              <h3 className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 pb-1">
                <span className="font-display text-base font-semibold leading-tight">
                  {group.label ?? "Scrutins sans dossier rattaché"}
                </span>
                <span className="tabular text-sm font-normal text-muted">
                  {pluralize(group.count, "scrutin")} · {pluralize(group.adopted, "adopté")} ·{" "}
                  {pluralize(group.rejected, "rejeté")}
                </span>
              </h3>
              <ul className="flex flex-col border-t border-rule">
                {group.scrutins.map((scrutin) => (
                  <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={scrutin.counts ?? undefined} />
                ))}
              </ul>
            </section>
          ))}
          {week.hiddenGroups > 0 ? (
            <p className="text-sm text-muted">Et {week.hiddenGroups} autres dossiers votés cette semaine.</p>
          ) : null}
        </div>
      )}
    </section>
  );
};
