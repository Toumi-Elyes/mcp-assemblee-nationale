import "server-only";
import { cache } from "react";
import {
  getScrutinVotes,
  getStatements,
  listDeputesPage,
  listGroupes,
} from "@/lib/civix/api";
import { toPosition, toResult, toDay } from "@/lib/civix/mappers";
import type { Counts, Dossier, Position, VoteResult } from "@/lib/civix/types";
import { cleanTitle } from "@/lib/text";
import { settle } from "./result";
import { firstAssembleeUrl, safeUrl } from "@/lib/civix/urls";
import { CIVIX_SITE } from "@/lib/config";

export type VoteRow = {
  uid: string;
  name: string;
  position: Position;
  byDelegation: boolean;
  groupAbbr: string | null;
};

export type GroupBreakdown = { abbr: string | null; label: string; counts: Counts };

export type StatementView = {
  abbr: string | null;
  label: string;
  position: string | null;
  text: string;
};

export type ScrutinPageData = {
  uid: string;
  numero: number | null;
  legislature: number | null;
  date: string | null;
  title: string;
  dossier: Dossier | null;
  result: VoteResult;
  resultLabel: string | null;
  voteType: string | null;
  majorityRule: string | null;
  voteMode: string | null;
  requestedBy: string | null;
  counts: Counts | null;
  byGroup: GroupBreakdown[];
  statements: StatementView[];
  statementsAvailable: boolean;
  votes: VoteRow[];
  groupOptions: string[];
  civixUrl: string;
  assembleeUrl: string | null;
};

const DIRECTORY_FIRST_PAGE = 1;
const DIRECTORY_MAX_PAGES = 20;

const getDirectory = cache(async (): Promise<Map<string, string>> => {
  const first = await listDeputesPage(DIRECTORY_FIRST_PAGE);
  const total = first.total ?? first.deputes.length;
  const pageCount = Math.min(Math.ceil(total / Math.max(first.deputes.length, 1)), DIRECTORY_MAX_PAGES);
  const rest = await Promise.all(
    Array.from({ length: Math.max(pageCount - 1, 0) }, (_, index) =>
      listDeputesPage(DIRECTORY_FIRST_PAGE + 1 + index),
    ),
  );
  const directory = new Map<string, string>();
  for (const page of [first, ...rest]) {
    for (const depute of page.deputes) {
      if (depute.groupAbbr !== null) {
        directory.set(depute.uid, depute.groupAbbr);
      }
    }
  }
  return directory;
});

export const getScrutinPage = cache(async (uid: string): Promise<ScrutinPageData> => {
  const response = await getScrutinVotes(uid);
  const attributes = response.data.attributes;
  const scrutin = attributes.scrutin;
  const [groupes, statements] = await Promise.all([settle(listGroupes()), settle(getStatements(uid))]);

  const groupList = groupes.ok ? groupes.data : [];
  const byUid = new Map(groupList.map((groupe) => [groupe.uid, groupe]));
  const currentLegislature = groupList[0]?.legislature ?? null;
  const isCurrent = currentLegislature !== null && scrutin.legislature === currentLegislature;
  const directory = isCurrent ? await settle(getDirectory()) : { ok: false as const };
  const memberGroups = directory.ok ? directory.data : new Map<string, string>();

  const votes: VoteRow[] = attributes.votes.map((vote) => ({
    uid: vote.deputy_uid,
    name: `${vote.prenom} ${vote.nom}`.trim(),
    position: toPosition(vote.position),
    byDelegation: vote.par_delegation,
    groupAbbr: memberGroups.get(vote.deputy_uid) ?? null,
  }));

  const groupOptions = directory.ok
    ? [...new Set(votes.flatMap((vote) => (vote.groupAbbr === null ? [] : [vote.groupAbbr])))].sort(
        (a, b) => a.localeCompare(b),
      )
    : [];

  const byGroup: GroupBreakdown[] = attributes.results_by_group.map((row) => {
    const groupe = byUid.get(row.groupe_uid);
    return { abbr: groupe?.abbr ?? null, label: groupe?.label ?? "Groupe non identifié", counts: row };
  });

  const statementRows = statements.ok
    ? statements.data
        .filter((item) => item.status === undefined || item.status === null || item.status === "approved")
        .map((item) => ({
          abbr: item.groupe_abrev ?? null,
          label: item.groupe_libelle ?? item.groupe_abrev ?? "Groupe",
          position: item.vote_position ?? null,
          text: item.statement,
        }))
    : [];

  return {
    uid: scrutin.uid,
    numero: scrutin.numero ?? null,
    legislature: scrutin.legislature ?? null,
    date: toDay(scrutin.date_scrutin),
    title: cleanTitle(scrutin.titre),
    dossier: dossierOf(scrutin.objet?.dossierLegislatif),
    result: toResult(scrutin.sort_code, scrutin.is_adopted),
    resultLabel: scrutin.official_result ?? scrutin.sort_libelle ?? null,
    voteType: scrutin.type_vote?.libelleTypeVote ?? null,
    majorityRule: scrutin.majority_rule ?? null,
    voteMode: scrutin.vote_mode ?? null,
    requestedBy: scrutin.demandeur?.texte ?? null,
    counts: attributes.results_global ?? null,
    byGroup,
    statements: statementRows,
    statementsAvailable: statements.ok,
    votes,
    groupOptions,
    civixUrl: safeUrl(response.source?.civix_urls["page"], `${CIVIX_SITE}/votes/${scrutin.uid}`),
    assembleeUrl: firstAssembleeUrl(response.source?.source_urls ?? []),
  };
});

function dossierOf(
  dossier: { libelle?: string | null; dossierRef?: string | null } | null | undefined,
): Dossier | null {
  const label = dossier?.libelle?.trim();
  if (label === undefined || label === "") {
    return null;
  }
  return { key: dossier?.dossierRef ?? label, label };
}
