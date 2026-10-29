import "server-only";
import type { z } from "zod";
import { REVALIDATE_SECONDS } from "@/lib/config";

const DEFAULT_BASE_URL = "https://www.civix.fr/api/v1";
const TIMEOUT_MS = 15_000;

export class CivixError extends Error {
  readonly status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "CivixError";
    this.status = status;
  }
}

export type Params = Record<string, string | number | undefined>;

function baseUrl(): string {
  const configured = process.env.CIVIX_BASE_URL;
  return (configured !== undefined && configured !== "" ? configured : DEFAULT_BASE_URL).replace(
    /\/$/,
    "",
  );
}

function buildUrl(path: string, params: Params): string {
  const url = new URL(`${baseUrl()}${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

export async function civixGet<Schema extends z.ZodType>(
  path: string,
  params: Params,
  schema: Schema,
  revalidate: number = REVALIDATE_SECONDS,
  timeoutMs: number = TIMEOUT_MS,
): Promise<z.infer<Schema>> {
  let response: Response;
  try {
    response = await fetch(buildUrl(path, params), {
      headers: { accept: "application/json" },
      signal: AbortSignal.timeout(timeoutMs),
      next: { revalidate },
    });
  } catch {
    throw new CivixError("CIVIX injoignable");
  }
  if (!response.ok) {
    throw new CivixError(`CIVIX a répondu ${response.status}`, response.status);
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new CivixError("Réponse CIVIX illisible");
  }
  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new CivixError("Réponse CIVIX inattendue");
  }
  return parsed.data;
}
