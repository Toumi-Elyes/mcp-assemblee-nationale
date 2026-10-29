import { z } from "zod";
import { ASSEMBLEE_SITE } from "@/lib/config";

const ALLOWED_HOSTS = /^(www\.assemblee-nationale\.fr|www\.civix\.fr|civix\.fr)$/;

const trustedUrl = z.url({ protocol: /^https$/, hostname: ALLOWED_HOSTS });

export function safeUrl(candidate: string | null | undefined, fallback: string): string {
  const parsed = trustedUrl.safeParse(candidate);
  return parsed.success ? parsed.data : fallback;
}

const SCRUTIN_UID = /^VTANR5L(\d{1,2})V\d{1,6}$/;

function positiveInteger(value: number | null | undefined): number | null {
  return typeof value === "number" && Number.isInteger(value) && value > 0 ? value : null;
}

function legislatureFromUid(uid: string): number | null {
  const match = SCRUTIN_UID.exec(uid);
  return match?.[1] !== undefined ? Number(match[1]) : null;
}

export function assembleeScrutinUrl(
  scrutin: { uid: string; legislature?: number | null; numero?: number | null },
): string | null {
  const numero = positiveInteger(scrutin.numero);
  const legislature = positiveInteger(scrutin.legislature) ?? legislatureFromUid(scrutin.uid);
  if (numero === null || legislature === null) {
    return null;
  }
  const parsed = trustedUrl.safeParse(`${ASSEMBLEE_SITE}/dyn/${legislature}/scrutins/${numero}`);
  return parsed.success ? parsed.data : null;
}
