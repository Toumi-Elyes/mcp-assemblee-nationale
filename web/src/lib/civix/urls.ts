import { z } from "zod";
import { ASSEMBLEE_SITE } from "@/lib/config";

const ALLOWED_HOSTS = /^(www\.assemblee-nationale\.fr|www\.civix\.fr|civix\.fr)$/;

const trustedUrl = z.url({ protocol: /^https$/, hostname: ALLOWED_HOSTS });

export function safeUrl(candidate: string | null | undefined, fallback: string): string {
  const parsed = trustedUrl.safeParse(candidate);
  return parsed.success ? parsed.data : fallback;
}

export function firstAssembleeUrl(candidates: readonly string[]): string | null {
  for (const candidate of candidates) {
    if (candidate.replace(/\/$/, "") === ASSEMBLEE_SITE) {
      continue;
    }
    const parsed = trustedUrl.safeParse(candidate);
    if (parsed.success) {
      return parsed.data;
    }
  }
  return null;
}
