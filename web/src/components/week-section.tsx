"use client";

import type { WeekScrutinView, WeekView } from "@/lib/data/view-types";
import { formatShortDay } from "@/lib/format";
import { normalizeSearch } from "@/lib/text";
import { Flap } from "./flap";
import { useLive } from "./live-context";
import { LiveStatus } from "./live-status";
import { BoardHead, ScrutinRow } from "./scrutin-row";
import { Unavailable } from "./unavailable";

const ROWS_SHOWN = 5;

type BoardRow = WeekScrutinView & { dossier: string | null };

function dossierLine(label: string | null, title: string): string | null {
  if (label === null || normalizeSearch(title).includes(normalizeSearch(label))) {
    return null;
  }
  return label;
}

function boardRows(week: WeekView): BoardRow[] {
  return week.groups
    .flatMap((group) =>
      group.scrutins.map((scrutin) => ({ ...scrutin, dossier: dossierLine(group.label, scrutin.title) })),
    )
    .sort((left, right) => (right.date ?? "").localeCompare(left.date ?? ""));
}

const Rows: React.FC<{ rows: readonly BoardRow[] }> = ({ rows }) => {
  return (
    <ul className="flex flex-col">
      {rows.map((row) => (
        <ScrutinRow key={row.uid} scrutin={row} counts={row.counts ?? undefined} dossier={row.dossier} />
      ))}
    </ul>
  );
};

export const WeekSection: React.FC = () => {
  const { snapshot } = useLive();
  const { week } = snapshot;
  const rows = week !== null ? boardRows(week) : [];
  const first = rows.slice(0, ROWS_SHOWN);
  const rest = rows.slice(ROWS_SHOWN);
  return (
    <section aria-labelledby="semaine-titre" className="flex flex-col gap-3">
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
              Du {formatShortDay(week.from)} au {formatShortDay(week.to)}, les plus récents en premier.
            </p>
          ) : null}
          <LiveStatus />
        </div>
      </header>
      {week === null ? (
        <Unavailable />
      ) : (
        <div className="flex flex-col gap-3">
          <BoardHead />
          <Rows rows={first} />
          {rest.length > 0 ? (
            <details className="group">
              <summary className="cursor-pointer list-none py-2 font-display text-base font-semibold text-accent transition-colors hover:text-accent-hover">
                <span className="group-open:hidden">Afficher {rest.length} autres scrutins de la semaine</span>
                <span className="hidden group-open:inline">Masquer les autres scrutins</span>
              </summary>
              <Rows rows={rest} />
            </details>
          ) : null}
          {rows.length < week.total ? (
            <p className="text-sm text-muted">
              {rows.length} scrutins listés sur {week.total} cette semaine
              {week.hiddenGroups > 0 ? `, dans ${week.hiddenGroups + week.groups.length} dossiers` : ""}.
            </p>
          ) : null}
        </div>
      )}
    </section>
  );
};
