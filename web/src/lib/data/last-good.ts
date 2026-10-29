import { PHASE_PRODUCTION_BUILD } from "next/constants";

export function keepLastGoodVersion(nothingLoaded: boolean): void {
  if (nothingLoaded && process.env.NEXT_PHASE !== PHASE_PRODUCTION_BUILD) {
    throw new Error("CIVIX indisponible : la dernière version valide reste servie.");
  }
}

export function isEmptyView(view: {
  week: unknown;
  trends: unknown;
  groupes: unknown;
  counters: { scrutins: number | null };
}): boolean {
  return view.week === null && view.trends === null && view.groupes === null && view.counters.scrutins === null;
}
