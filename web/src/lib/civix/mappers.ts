import { cleanTitle, isFinalVoteTitle } from "@/lib/text";
import { CIVIX_SITE, ASSEMBLEE_SITE } from "@/lib/config";
import { safeUrl } from "./urls";
import type {
  DeputeDto,
  GroupeDto,
  ScrutinSummaryDto,
} from "./schemas";
import type { Depute, Groupe, Position, Scrutin, VoteResult } from "./types";

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}/;

export function toDay(value: string | null | undefined): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  const match = DATE_PATTERN.exec(value);
  return match ? match[0] : null;
}

export function toResult(code: string | null | undefined, isAdopted?: boolean | null): VoteResult {
  if (code === "adopté") {
    return "adopte";
  }
  if (code === "rejeté") {
    return "rejete";
  }
  if (isAdopted === true) {
    return "adopte";
  }
  if (isAdopted === false) {
    return "rejete";
  }
  return "inconnu";
}

function isPosition(value: string): value is Position {
  return value === "pour" || value === "contre" || value === "abstention" || value === "non_votant";
}

export function toPosition(value: string): Position {
  return isPosition(value) ? value : "unknown";
}

export function toScrutin(dto: ScrutinSummaryDto): Scrutin {
  const dossier = dto.objet?.dossierLegislatif;
  const label = dossier?.libelle?.trim();
  const key = dossier?.dossierRef ?? label;
  return {
    uid: dto.uid,
    legislature: dto.legislature ?? null,
    numero: dto.numero ?? null,
    date: toDay(dto.date_scrutin),
    title: cleanTitle(dto.titre),
    dossier: label !== undefined && label !== "" && key ? { key, label } : null,
    result: toResult(dto.sort?.code),
    type: dto.type ?? null,
    isFinalVote: isFinalVoteTitle(dto.titre),
  };
}

export function toGroupe(dto: GroupeDto): Groupe {
  return {
    uid: dto.uid,
    abbr: dto.abbr,
    label: dto.libelle,
    size: dto.effectif ?? 0,
    legislature: dto.legislature ?? null,
    url: dto.urls?.page !== undefined && dto.urls.page !== null ? safeUrl(dto.urls.page, `${CIVIX_SITE}/groupes`) : null,
  };
}

export function toDepute(dto: DeputeDto): Depute {
  const fullName = `${dto.prenom} ${dto.nom}`.trim();
  return {
    uid: dto.uid,
    firstName: dto.prenom,
    lastName: dto.nom,
    fullName,
    groupAbbr: dto.groupe_abrev ?? null,
    groupLabel: dto.groupe_libelle ?? null,
    department: dto.circ_departement ?? null,
    civixUrl: safeUrl(dto.urls?.civix_page, `${CIVIX_SITE}/deputes/${dto.uid}`),
    assembleeUrl: safeUrl(dto.urls?.assemblee, `${ASSEMBLEE_SITE}/dyn/deputes/${dto.uid}`),
  };
}
