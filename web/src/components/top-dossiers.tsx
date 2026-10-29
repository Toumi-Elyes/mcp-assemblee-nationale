"use client";

import { useState } from "react";
import { formatNumber, formatShortDay } from "@/lib/format";

export type TopDossierItem = {
  key: string;
  label: string;
  total: number;
  adopted: number;
  rejected: number;
};

export type TopDossierPeriod = {
  id: string;
  label: string;
  from: string;
  to: string;
  complete: boolean;
  items: TopDossierItem[];
};

export const TopDossiers: React.FC<{ periods: TopDossierPeriod[] }> = ({ periods }) => {
  const [selected, setSelected] = useState(periods[0]?.id ?? "");
  const period = periods.find((item) => item.id === selected) ?? periods[0];
  if (period === undefined) {
    return null;
  }
  const peak = Math.max(...period.items.map((item) => item.total), 1);

  return (
    <div>
      <div role="group" aria-label="Période" className="mb-4 inline-flex rounded-lg border border-line p-0.5">
        {periods.map((item) => {
          const onSelect = () => {
            setSelected(item.id);
          };
          return (
            <button
              key={item.id}
              type="button"
              onClick={onSelect}
              aria-pressed={item.id === period.id}
              className={`rounded-md px-3 py-1.5 text-sm font-semibold ${
                item.id === period.id ? "bg-accent text-accent-ink" : "text-muted hover:text-ink"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      <p className="mb-3 text-sm text-muted">
        Du {formatShortDay(period.from)} au {formatShortDay(period.to)}
        {period.complete ? "" : " (période limitée aux votes récupérés)"}.
      </p>
      {period.items.length === 0 ? (
        <p className="text-muted">Aucun scrutin sur cette période.</p>
      ) : (
        <ol className="space-y-3">
          {period.items.map((item) => (
            <li key={item.key}>
              <div className="flex items-baseline justify-between gap-3">
                <span className="text-sm font-medium">{item.label}</span>
                <span className="whitespace-nowrap text-sm tabular-nums text-muted">
                  {formatNumber(item.total)} scrutins
                </span>
              </div>
              <div
                role="img"
                aria-label={`${item.total} scrutins, dont ${item.adopted} adoptés et ${item.rejected} rejetés`}
                className="mt-1 h-2 overflow-hidden rounded-full bg-surface-2"
              >
                <div
                  className="h-full rounded-full"
                  style={{ width: `${(item.total / peak) * 100}%`, background: "var(--bar)" }}
                />
              </div>
              <p className="mt-0.5 text-xs text-muted">
                {formatNumber(item.adopted)} adoptés · {formatNumber(item.rejected)} rejetés
              </p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
};
