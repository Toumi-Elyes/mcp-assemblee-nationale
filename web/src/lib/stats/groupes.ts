import type { Groupe } from "@/lib/civix/types";

export type GroupShare = { groupe: Groupe; share: number };

export function totalSeats(groupes: readonly Groupe[]): number {
  return groupes.reduce((sum, groupe) => sum + groupe.size, 0);
}

export function groupShares(groupes: readonly Groupe[]): GroupShare[] {
  const total = totalSeats(groupes);
  return [...groupes]
    .sort((a, b) => b.size - a.size || a.abbr.localeCompare(b.abbr))
    .map((groupe) => ({ groupe, share: total === 0 ? 0 : groupe.size / total }));
}
