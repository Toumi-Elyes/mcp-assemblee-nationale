import "server-only";
import { cache } from "react";
import { settle } from "./result";
import {
  listDeputesPage,
  listGroupes,
  listScrutins,
  getScrutinDetail,
  getScrutinVotes,
  type ScrutinPage,
} from "@/lib/civix/api";
import type { Counts, Depute, Groupe, Scrutin } from "@/lib/civix/types";
import {
  addDays,
  dayKey,
  dayOfYear,
  latestFinalVotes,
  oldestDate,
  totalSeats,
} from "@/lib/stats";

const MAX_TREND_PAGES = 10;
const PAGES_PER_BATCH = 4;
const TREND_DAYS = 30;
const FINAL_VOTES_SHOWN = 6;
const FINAL_VOTES_SEARCH = "ensemble";
const SUGGESTED_TOPICS = 3;
const TOPIC_CANDIDATES = 5;
const SUGGESTED_DEPUTES = 4;
const DEPUTES_PER_PAGE = 50;

export type Pool = {
  scrutins: Scrutin[];
  exhausted: boolean;
  legislature: number | null;
  legislatureTotal: number | null;
};

async function fetchPages(first: ScrutinPage, cutoff: string) {
  const scrutins = [...first.scrutins];
  let hasNext = first.hasNext;
  let page = 1;
  while (hasNext && page < MAX_TREND_PAGES && (oldestDate(scrutins) ?? "") > cutoff) {
    const wanted = Array.from(
      { length: Math.min(PAGES_PER_BATCH, MAX_TREND_PAGES - page) },
      (_, index) => page + 1 + index,
    );
    const settled = await Promise.allSettled(wanted.map((number) => listScrutins({ page: number })));
    let failed = false;
    for (const outcome of settled) {
      if (outcome.status === "rejected") {
        failed = true;
        break;
      }
      scrutins.push(...outcome.value.scrutins);
      hasNext = outcome.value.hasNext;
      page += 1;
    }
    if (failed) {
      return { scrutins, hasNext: true };
    }
  }
  return { scrutins, hasNext };
}

async function legislatureTotal(legislature: number | null): Promise<number | null> {
  if (legislature === null) {
    return null;
  }
  try {
    return (await listScrutins({ pageSize: 1, legislature })).total;
  } catch {
    return null;
  }
}

export const getPool = cache(async (): Promise<Pool> => {
  const first = await listScrutins({ page: 1 });
  const legislature = first.scrutins[0]?.legislature ?? null;
  const cutoff = addDays(dayKey(new Date()), -(TREND_DAYS - 1));
  const [{ scrutins, hasNext }, total] = await Promise.all([
    fetchPages(first, cutoff),
    legislatureTotal(legislature),
  ]);
  return { scrutins, exhausted: !hasNext, legislature, legislatureTotal: total };
});

export const getGroupes = cache(listGroupes);

export const getFinalVotes = cache(async (): Promise<Scrutin[]> => {
  const { legislature } = await getPool();
  const page = await listScrutins({
    search: FINAL_VOTES_SEARCH,
    legislature: legislature ?? undefined,
    pageSize: 30,
  });
  return latestFinalVotes(page.scrutins, FINAL_VOTES_SHOWN);
});

export type ScrutinCounts = Map<string, Counts>;

export async function getCounts(uids: readonly string[]): Promise<ScrutinCounts> {
  const unique = [...new Set(uids)];
  const settled = await Promise.allSettled(unique.map((uid) => getScrutinDetail(uid)));
  const counts: ScrutinCounts = new Map();
  settled.forEach((outcome, index) => {
    const uid = unique[index];
    if (uid === undefined || outcome.status === "rejected") {
      return;
    }
    const global = outcome.value.data.attributes.results_global;
    if (global) {
      counts.set(uid, global);
    }
  });
  return counts;
}

export type Suggestions = { topics: string[]; deputes: Depute[] };

async function verifiedTopics(finals: readonly Scrutin[]): Promise<string[]> {
  const candidates = [
    ...new Set(finals.flatMap((scrutin) => (scrutin.dossier === null ? [] : [scrutin.dossier.label]))),
  ].slice(0, TOPIC_CANDIDATES);
  const checks = await Promise.allSettled(
    candidates.map((label) => listScrutins({ search: label, pageSize: 1 })),
  );
  const topics: string[] = [];
  checks.forEach((outcome, index) => {
    const label = candidates[index];
    if (label !== undefined && outcome.status === "fulfilled" && outcome.value.scrutins.length > 0) {
      topics.push(label);
    }
  });
  return topics.slice(0, SUGGESTED_TOPICS);
}

async function voterUids(finals: readonly Scrutin[]): Promise<Set<string> | null> {
  const latest = finals[0];
  if (latest === undefined) {
    return null;
  }
  const response = await getScrutinVotes(latest.uid);
  return new Set(response.data.attributes.votes.map((vote) => vote.deputy_uid));
}

async function rotatingDeputes(groupes: readonly Groupe[], voters: Set<string> | null): Promise<Depute[]> {
  const pages = Math.max(1, Math.floor(totalSeats(groupes) / DEPUTES_PER_PAGE));
  const page = (dayOfYear(dayKey(new Date())) % pages) + 1;
  const { deputes } = await listDeputesPage(page);
  const seen = new Set<string>();
  const picked: Depute[] = [];
  for (const depute of deputes) {
    const group = depute.groupAbbr ?? "";
    if (!seen.has(group) && (voters === null || voters.has(depute.uid))) {
      seen.add(group);
      picked.push(depute);
    }
  }
  return picked.slice(0, SUGGESTED_DEPUTES);
}

export const getSuggestions = cache(async (): Promise<Suggestions> => {
  const [finals, groupes] = await Promise.all([getFinalVotes(), getGroupes()]);
  const voters = await settle(voterUids(finals));
  const [topics, deputes] = await Promise.allSettled([
    verifiedTopics(finals),
    rotatingDeputes(groupes, voters.ok ? voters.data : null),
  ]);
  return {
    topics: topics.status === "fulfilled" ? topics.value : [],
    deputes: deputes.status === "fulfilled" ? deputes.value : [],
  };
});
