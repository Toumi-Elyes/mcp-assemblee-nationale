import "server-only";
import { getDepute, getScrutinVotes, listScrutins, searchDeputes } from "@/lib/civix/api";
import { assembleeScrutinUrl, safeUrl } from "@/lib/civix/urls";
import { toPosition, toResult } from "@/lib/civix/mappers";
import type { Depute, Position, VoteResult } from "@/lib/civix/types";
import { CIVIX_SITE } from "@/lib/config";
import { cleanTitle, matchesName } from "@/lib/text";

export const MAX_DEMO_SCRUTINS = 5;
const DEMO_REVALIDATE = 600;
const DEMO_TIMEOUT_MS = 5_000;
const MAX_CANDIDATES = 8;

export type DemoEntry = {
  uid: string;
  date: string | null;
  title: string;
  dossier: string | null;
  result: VoteResult;
  position: Position;
  civixUrl: string;
  assembleeUrl: string | null;
};

export type DemoAnswer = {
  depute: Depute;
  topic: string;
  total: number | null;
  entries: DemoEntry[];
};

export async function findDeputeCandidates(query: string): Promise<Depute[]> {
  const hits = await searchDeputes(query, DEMO_TIMEOUT_MS);
  return hits.filter((depute) => matchesName(depute.fullName, query)).slice(0, MAX_CANDIDATES);
}

async function entryFor(deputeUid: string, uid: string): Promise<DemoEntry> {
  const response = await getScrutinVotes(uid, DEMO_TIMEOUT_MS);
  const attributes = response.data.attributes;
  const scrutin = attributes.scrutin;
  const vote = attributes.votes.find((item) => item.deputy_uid === deputeUid);
  return {
    uid,
    date: scrutin.date_scrutin?.slice(0, 10) ?? null,
    title: cleanTitle(scrutin.titre),
    dossier: scrutin.objet?.dossierLegislatif?.libelle ?? null,
    result: toResult(scrutin.sort_code, scrutin.is_adopted),
    position: vote ? toPosition(vote.position) : "unknown",
    civixUrl: safeUrl(response.source?.civix_urls["page"], `${CIVIX_SITE}/votes/${uid}`),
    assembleeUrl: assembleeScrutinUrl(scrutin),
  };
}

export async function commentAVote(deputeUid: string, topic: string): Promise<DemoAnswer> {
  const depute = await getDepute(deputeUid, DEMO_TIMEOUT_MS);
  const page = await listScrutins({
    search: topic,
    pageSize: MAX_DEMO_SCRUTINS,
    revalidate: DEMO_REVALIDATE,
    timeoutMs: DEMO_TIMEOUT_MS,
  });
  const entries = await Promise.all(
    page.scrutins.slice(0, MAX_DEMO_SCRUTINS).map((scrutin) => entryFor(deputeUid, scrutin.uid)),
  );
  return { depute, topic, total: page.total, entries };
}
