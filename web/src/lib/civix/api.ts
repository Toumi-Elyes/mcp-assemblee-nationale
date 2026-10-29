import "server-only";
import { civixGet } from "./client";
import { toDepute, toGroupe, toScrutin } from "./mappers";
import {
  deputeDetailSchema,
  deputesSchema,
  groupesSchema,
  scrutinDetailResponseSchema,
  scrutinListSchema,
  scrutinVotesSchema,
  searchSchema,
  statementsSchema,
} from "./schemas";
import type { Depute, Groupe, Scrutin } from "./types";

export const MAX_PAGE_SIZE = 50;
const DETAIL_REVALIDATE = 6 * 3600;
const DIRECTORY_REVALIDATE = 24 * 3600;
const SEARCH_REVALIDATE = 600;

export type ScrutinPage = { scrutins: Scrutin[]; total: number | null; hasNext: boolean };

type ScrutinQuery = {
  page?: number;
  pageSize?: number;
  legislature?: number;
  search?: string;
  revalidate?: number;
  timeoutMs?: number;
};

export async function listScrutins(query: ScrutinQuery = {}): Promise<ScrutinPage> {
  const response = await civixGet(
    "/scrutins",
    {
      page: query.page ?? 1,
      page_size: query.pageSize ?? MAX_PAGE_SIZE,
      legislature: query.legislature,
      search: query.search,
    },
    scrutinListSchema,
    query.revalidate,
    query.timeoutMs,
  );
  const pagination = response.meta?.pagination;
  return {
    scrutins: response.data.attributes.results.map(toScrutin),
    total: pagination?.count_total ?? null,
    hasNext: (pagination?.next_page ?? null) !== null,
  };
}

export async function getScrutinVotes(uid: string, timeoutMs?: number) {
  return civixGet(
    `/scrutins/${encodeURIComponent(uid)}/votes`,
    {},
    scrutinVotesSchema,
    DETAIL_REVALIDATE,
    timeoutMs,
  );
}

export async function getScrutinDetail(uid: string) {
  return civixGet(`/scrutins/${encodeURIComponent(uid)}`, {}, scrutinDetailResponseSchema, DETAIL_REVALIDATE);
}

export async function getStatements(uid: string) {
  const response = await civixGet(
    `/scrutins/${encodeURIComponent(uid)}/statements`,
    {},
    statementsSchema,
    DETAIL_REVALIDATE,
  );
  return response.data.attributes.statements;
}

export async function listGroupes(): Promise<Groupe[]> {
  const response = await civixGet("/groupes", {}, groupesSchema, DIRECTORY_REVALIDATE);
  return response.data.attributes.groups.map(toGroupe);
}

export type DeputesPage = { deputes: Depute[]; total: number | null };

export async function listDeputesPage(page: number): Promise<DeputesPage> {
  const response = await civixGet(
    "/deputes",
    { page, page_size: MAX_PAGE_SIZE },
    deputesSchema,
    DIRECTORY_REVALIDATE,
  );
  const pagination = response.meta?.pagination;
  return {
    deputes: response.data.attributes.results.map(toDepute),
    total: pagination?.count_total ?? pagination?.count_estimated ?? null,
  };
}

export async function getDepute(uid: string, timeoutMs?: number): Promise<Depute> {
  const response = await civixGet(
    `/deputes/${encodeURIComponent(uid)}`,
    {},
    deputeDetailSchema,
    DIRECTORY_REVALIDATE,
    timeoutMs,
  );
  return toDepute(response.data.attributes.deputy);
}

export async function searchDeputes(query: string, timeoutMs?: number): Promise<Depute[]> {
  const response = await civixGet("/search", { search: query }, searchSchema, SEARCH_REVALIDATE, timeoutMs);
  return response.results.deputes.map((hit) =>
    toDepute({
      uid: hit.acteur_uid,
      prenom: hit.prenom,
      nom: hit.nom,
      groupe_abrev: hit.groupe_libelle_abrev,
      circ_departement: hit.circ_departement,
    }),
  );
}
