import type { NextRequest } from "next/server";
import { z } from "zod";
import { errorResponse, okResponse, rejectCrossSite } from "@/lib/api-guard";
import { findDeputeCandidates } from "@/lib/data/demo";

const querySchema = z.object({
  q: z
    .string()
    .trim()
    .min(2)
    .max(100)
    .transform((value) => value.toLowerCase().replace(/\s+/g, " ")),
});

export async function GET(request: NextRequest) {
  const blocked = rejectCrossSite(request);
  if (blocked !== null) {
    return blocked;
  }
  const parsed = querySchema.safeParse({ q: request.nextUrl.searchParams.get("q") ?? "" });
  if (!parsed.success) {
    return errorResponse("Saisissez au moins 2 lettres.", 400);
  }
  try {
    return okResponse({ deputes: await findDeputeCandidates(parsed.data.q) });
  } catch {
    return errorResponse("Données momentanément indisponibles.", 502);
  }
}
