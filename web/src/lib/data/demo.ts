import "server-only";
import { getDepute, getScrutinVotes, listScrutins, searchDeputes } from "@/lib/civix/api";
import { toPosition, toResult } from "@/lib/civix/mappers";
import type { Depute, Position, VoteResult } from "@/lib/civix/types";
import { ASSEMBLEE_SITE, CIVIX_SITE } from "@/lib/config";
import { cleanTitle, matchesName } from "@/lib/text";

export const MAX_DEMO_SCRUTINS = 5;
const DEMO_REVALIDATE = 600;
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
  const hits = await searchDeputes(query);
  return hits.filter((depute) => matchesName(depute.fullName, query)).slice(0, MAX_CANDIDATES);
}

async function entryFor(deputeUid: string, uid: string): Promise<DemoEntry> {
  const response = await getScrutinVotes(uid);
  const attributes = response.data.attributes;
  const scrutin = attributes.scrutin;
  const vote = attributes.votes.find((item) => item.deputy_uid === deputeUid);
  const assembleeUrl =
    response.source?.source_urls.find((url) => url.replace(/\/$/, "") !== ASSEMBLEE_SITE) ?? null;
  return {
    uid,
    date: scrutin.date_scrutin?.slice(0, 10) ?? null,
    title: cleanTitle(scrutin.titre),
    dossier: scrutin.objet?.dossierLegislatif?.libelle ?? null,
    result: toResult(scrutin.sort_code, scrutin.is_adopted),
    position: vote ? toPosition(vote.position) : "unknown",
    civixUrl: response.source?.civix_urls["page"] ?? `${CIVIX_SITE}/votes/${uid}`,
    assembleeUrl,
  };
}

export async function commentAVote(deputeUid: string, topic: string): Promise<DemoAnswer> {
  const [depute, page] = await Promise.all([
    getDepute(deputeUid),
    listScrutins({ search: topic, pageSize: MAX_DEMO_SCRUTINS, revalidate: DEMO_REVALIDATE }),
  ]);
  const entries = await Promise.all(
    page.scrutins.slice(0, MAX_DEMO_SCRUTINS).map((scrutin) => entryFor(deputeUid, scrutin.uid)),
  );
  return { depute, topic, total: page.total, entries };
}
