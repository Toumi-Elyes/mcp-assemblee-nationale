"use client";

import { useState } from "react";
import { cn } from "@/lib/cn";
import { endSentence, formatShortDay, pluralize } from "@/lib/format";
import type { TopDossierPeriod } from "@/lib/data/view-types";

export const TopDossiers: React.FC<{ periods: readonly TopDossierPeriod[] }> = ({ periods }) => {
  const [selected, setSelected] = useState(periods[0]?.id ?? "");
  const period = periods.find((item) => item.id === selected) ?? periods[0];
  if (period === undefined) {
    return null;
  }
  const peak = Math.max(1, ...period.items.map((item) => item.total));
  return (
    <div className="flex flex-col gap-3">
      <div role="tablist" aria-label="Période" className="flex gap-0 self-start border-b border-line">
        {periods.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            id={`periode-${item.id}`}
            aria-selected={item.id === period.id}
            aria-controls="periode-panneau"
            onClick={() => {
              setSelected(item.id);
            }}
            className={cn(
              "-mb-px border-b-2 px-3 py-1.5 font-display text-base font-semibold transition-colors",
              item.id === period.id ? "border-rule text-ink" : "border-transparent text-muted hover:text-accent",
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div id="periode-panneau" role="tabpanel" aria-labelledby={`periode-${period.id}`} className="flex flex-col gap-3">
        {period.items.length === 0 ? (
          <p className="text-sm text-muted">Aucun dossier rattaché aux scrutins de cette période.</p>
        ) : (
          <ol className="flex flex-col gap-3">
            {period.items.map((item) => (
              <li key={item.key} className="flex flex-col gap-1">
                <div className="flex items-baseline justify-between gap-3">
                  <span className="text-sm font-medium">{item.label}</span>
                  <span className="tabular font-display text-lg font-semibold">{item.total}</span>
                </div>
                <svg role="img" aria-label={`${item.total} scrutins, ${item.adopted} adoptés, ${item.rejected} rejetés`} className="h-2.5 w-full" preserveAspectRatio="none">
                  <rect width="100%" height="100%" className="fill-absent" />
                  <rect width={`${(item.total / peak) * 100}%`} height="100%" className="fill-ink" />
                </svg>
                <span className="text-xs text-muted">
                  {pluralize(item.adopted, "adopté")}, {pluralize(item.rejected, "rejeté")}
                </span>
              </li>
            ))}
          </ol>
        )}
        <p className="text-xs text-muted">
          {endSentence(`Du ${formatShortDay(period.from)} au ${formatShortDay(period.to)}`)}
          {period.complete ? "" : " Période partielle : seuls les scrutins les plus récents ont pu être lus."}
        </p>
      </div>
    </div>
  );
};
