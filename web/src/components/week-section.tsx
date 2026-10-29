"use client";

import { CheckCircleIcon, XCircleIcon } from "@phosphor-icons/react";
import { formatShortDay, pluralize } from "@/lib/format";
import { ScrutinRow } from "./scrutin-row";
import { useLive } from "./live-context";

export const WeekSection: React.FC = () => {
  const { snapshot } = useLive();
  const { week } = snapshot;
  if (week === null) {
    return null;
  }
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-2xl font-bold">Cette semaine à l'Assemblée</h3>
        <p className="max-w-hero text-base text-muted">
          <span className="tabular font-bold text-ink">{week.total}</span> scrutins du {formatShortDay(week.from)} au{" "}
          {formatShortDay(week.to)}, regroupés par dossier.
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {week.groups.map((group) => (
          <div key={group.key}>
            <article className="flex h-full flex-col gap-3 rounded-lg border border-line bg-raised p-2">
              <header className="flex flex-col gap-2 p-3">
                <h4 className="text-lg font-bold">{group.label ?? "Scrutins sans dossier rattaché"}</h4>
                <p className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
                  <span className="tabular">{pluralize(group.count, "scrutin")}</span>
                  <span className="inline-flex items-center gap-1">
                    <CheckCircleIcon aria-hidden="true" size={16} weight="bold" />
                    {pluralize(group.adopted, "adopté")}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <XCircleIcon aria-hidden="true" size={16} weight="bold" />
                    {pluralize(group.rejected, "rejeté")}
                  </span>
                </p>
              </header>
              <ul className="flex flex-col gap-2">
                {group.scrutins.map((scrutin) => (
                  <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={scrutin.counts ?? undefined} />
                ))}
              </ul>
            </article>
          </div>
        ))}
      </div>
      {week.hiddenGroups > 0 ? <p className="text-sm text-muted">Et {week.hiddenGroups} autres dossiers votés cette semaine.</p> : null}
    </div>
  );
};
