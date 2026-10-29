import type { Dossier, Scrutin } from "@/lib/civix/types";
import { addDays, daysBetween, dayKey } from "./dates";

export type Coverage = {
  from: string;
  to: string;
  complete: boolean;
};

export type DayCount = { date: string; count: number };

export type VotesPerDay = {
  days: DayCount[];
  total: number;
  coverage: Coverage;
};

export type DossierStat = {
  dossier: Dossier;
  total: number;
  adopted: number;
  rejected: number;
  lastDate: string;
};

export type VoteKind = "ensemble" | "amendement" | "article" | "texte" | "autre";

export type KindStat = {
  kind: VoteKind;
  total: number;
  adopted: number;
  rejected: number;
  adoptionRate: number | null;
};

export type DossierGroup = {
  dossier: Dossier | null;
  scrutins: Scrutin[];
  adopted: number;
  rejected: number;
  lastDate: string;
};

type Dated = Scrutin & { date: string };

function hasDate(scrutin: Scrutin): scrutin is Dated {
  return scrutin.date !== null;
}

export function oldestDate(scrutins: readonly Scrutin[]): string | null {
  let oldest: string | null = null;
  for (const scrutin of scrutins) {
    if (scrutin.date !== null && (oldest === null || scrutin.date < oldest)) {
      oldest = scrutin.date;
    }
  }
  return oldest;
}

export function newestDate(scrutins: readonly Scrutin[]): string | null {
  let newest: string | null = null;
  for (const scrutin of scrutins) {
    if (scrutin.date !== null && (newest === null || scrutin.date > newest)) {
      newest = scrutin.date;
    }
  }
  return newest;
}

export function windowCoverage(
  scrutins: readonly Scrutin[],
  now: Date,
  days: number,
  exhausted: boolean,
): Coverage {
  const to = dayKey(now);
  const wantedFrom = addDays(to, -(days - 1));
  const oldest = oldestDate(scrutins);
  if (exhausted || oldest === null || oldest <= wantedFrom) {
    return { from: wantedFrom, to, complete: true };
  }
  return { from: addDays(oldest, 1), to, complete: false };
}

export function inWindow(scrutins: readonly Scrutin[], coverage: Coverage): Dated[] {
  return scrutins
    .filter(hasDate)
    .filter((scrutin) => scrutin.date >= coverage.from && scrutin.date <= coverage.to);
}

export function votesPerDay(
  scrutins: readonly Scrutin[],
  now: Date,
  days: number,
  exhausted = false,
): VotesPerDay {
  const coverage = windowCoverage(scrutins, now, days, exhausted);
  const counts = new Map<string, number>();
  for (const scrutin of inWindow(scrutins, coverage)) {
    counts.set(scrutin.date, (counts.get(scrutin.date) ?? 0) + 1);
  }
  const length = daysBetween(coverage.from, coverage.to) + 1;
  const series: DayCount[] = Array.from({ length }, (_, index) => {
    const date = addDays(coverage.from, index);
    return { date, count: counts.get(date) ?? 0 };
  });
  const total = series.reduce((sum, day) => sum + day.count, 0);
  return { days: series, total, coverage };
}

export function topDossiers(
  scrutins: readonly Scrutin[],
  now: Date,
  days: number,
  limit: number,
  exhausted = false,
): { items: DossierStat[]; coverage: Coverage } {
  const coverage = windowCoverage(scrutins, now, days, exhausted);
  const stats = new Map<string, DossierStat>();
  for (const scrutin of inWindow(scrutins, coverage)) {
    if (scrutin.dossier === null) {
      continue;
    }
    const current = stats.get(scrutin.dossier.key) ?? {
      dossier: scrutin.dossier,
      total: 0,
      adopted: 0,
      rejected: 0,
      lastDate: scrutin.date,
    };
    current.total += 1;
    current.adopted += scrutin.result === "adopte" ? 1 : 0;
    current.rejected += scrutin.result === "rejete" ? 1 : 0;
    current.lastDate = scrutin.date > current.lastDate ? scrutin.date : current.lastDate;
    stats.set(scrutin.dossier.key, current);
  }
  const items = [...stats.values()]
    .sort((a, b) => b.total - a.total || b.lastDate.localeCompare(a.lastDate))
    .slice(0, limit);
  return { items, coverage };
}

export function voteKind(scrutin: Scrutin): VoteKind {
  if (scrutin.isFinalVote) {
    return "ensemble";
  }
  if (scrutin.type === "amendement" || scrutin.type === "article" || scrutin.type === "texte") {
    return scrutin.type;
  }
  return "autre";
}

const KIND_ORDER: readonly VoteKind[] = ["ensemble", "texte", "article", "amendement", "autre"];

export function adoptionByKind(scrutins: readonly Scrutin[]): KindStat[] {
  const stats = new Map<VoteKind, KindStat>();
  for (const scrutin of scrutins) {
    if (scrutin.result === "inconnu") {
      continue;
    }
    const kind = voteKind(scrutin);
    const current = stats.get(kind) ?? { kind, total: 0, adopted: 0, rejected: 0, adoptionRate: null };
    current.total += 1;
    current.adopted += scrutin.result === "adopte" ? 1 : 0;
    current.rejected += scrutin.result === "rejete" ? 1 : 0;
    current.adoptionRate = current.adopted / current.total;
    stats.set(kind, current);
  }
  return KIND_ORDER.flatMap((kind) => {
    const stat = stats.get(kind);
    return stat ? [stat] : [];
  });
}

export function lastDays(scrutins: readonly Scrutin[], days: number): Dated[] {
  const newest = newestDate(scrutins);
  if (newest === null) {
    return [];
  }
  const from = addDays(newest, -(days - 1));
  return scrutins.filter(hasDate).filter((scrutin) => scrutin.date >= from);
}

export function groupByDossier(scrutins: readonly Dated[]): DossierGroup[] {
  const groups = new Map<string, DossierGroup>();
  for (const scrutin of scrutins) {
    const key = scrutin.dossier?.key ?? "__sans_dossier__";
    const group = groups.get(key) ?? {
      dossier: scrutin.dossier,
      scrutins: [],
      adopted: 0,
      rejected: 0,
      lastDate: scrutin.date,
    };
    group.scrutins.push(scrutin);
    group.adopted += scrutin.result === "adopte" ? 1 : 0;
    group.rejected += scrutin.result === "rejete" ? 1 : 0;
    group.lastDate = scrutin.date > group.lastDate ? scrutin.date : group.lastDate;
    groups.set(key, group);
  }
  return [...groups.values()].sort(
    (a, b) => b.lastDate.localeCompare(a.lastDate) || b.scrutins.length - a.scrutins.length,
  );
}

export function latestFinalVotes(scrutins: readonly Scrutin[], limit: number): Scrutin[] {
  return scrutins
    .filter((scrutin) => scrutin.isFinalVote && scrutin.date !== null)
    .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? "") || (b.numero ?? 0) - (a.numero ?? 0))
    .slice(0, limit);
}

export function shownScrutins(group: DossierGroup, perGroup: number): Scrutin[] {
  return [...group.scrutins]
    .sort(
      (a, b) =>
        Number(b.isFinalVote) - Number(a.isFinalVote) ||
        (b.date ?? "").localeCompare(a.date ?? "") ||
        (b.numero ?? 0) - (a.numero ?? 0),
    )
    .slice(0, perGroup);
}

export function countTargets(groups: readonly DossierGroup[], perGroup: number, max: number): string[] {
  return groups
    .flatMap((group) => shownScrutins(group, perGroup).map((scrutin) => scrutin.uid))
    .slice(0, max);
}

export function dayOfYear(key: string): number {
  return daysBetween(`${key.slice(0, 4)}-01-01`, key) + 1;
}
