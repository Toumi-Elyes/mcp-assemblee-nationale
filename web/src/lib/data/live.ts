import { shownScrutins } from "@/lib/stats";
import type { HomeView, LiveSnapshot, WeekData, WeekView } from "./view-types";

export const WEEK_DOSSIERS_SHOWN = 6;
export const WEEK_SCRUTINS_PER_DOSSIER = 3;

export function toWeekView(week: WeekData): WeekView {
  const shown = week.groups.slice(0, WEEK_DOSSIERS_SHOWN);
  return {
    from: week.from,
    to: week.to,
    total: week.total,
    hiddenGroups: week.groups.length - shown.length,
    groups: shown.map((group) => ({
      key: group.dossier?.key ?? "sans-dossier",
      label: group.dossier?.label ?? null,
      count: group.scrutins.length,
      adopted: group.adopted,
      rejected: group.rejected,
      scrutins: shownScrutins(group, WEEK_SCRUTINS_PER_DOSSIER).map((scrutin) => ({
        uid: scrutin.uid,
        date: scrutin.date,
        title: scrutin.title,
        result: scrutin.result,
        counts: week.counts.get(scrutin.uid) ?? null,
      })),
    })),
  };
}

export function buildLiveSnapshot(view: HomeView): LiveSnapshot {
  return {
    generatedAt: view.generatedAt.toISOString(),
    counters: view.counters,
    week: view.week !== null ? toWeekView(view.week) : null,
  };
}
