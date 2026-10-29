import type { NextRequest } from "next/server";
import { z } from "zod";
import { CivixError } from "@/lib/civix";
import { errorResponse, okResponse, rejectCrossSite } from "@/lib/api-guard";
import { commentAVote } from "@/lib/data/demo";

const MAX_TOPIC_LENGTH = 80;

const querySchema = z.object({
  depute: z.string().regex(/^PA\d{3,12}$/i, "Identifiant de député invalide"),
  sujet: z
    .string()
    .trim()
    .min(2, "Indiquez un sujet")
    .max(MAX_TOPIC_LENGTH, "Sujet trop long")
    .transform((value) => value.toLowerCase().replace(/\s+/g, " ")),
});

export async function GET(request: NextRequest) {
  const blocked = rejectCrossSite(request);
  if (blocked !== null) {
    return blocked;
  }
  const params = request.nextUrl.searchParams;
  const parsed = querySchema.safeParse({
    depute: params.get("depute") ?? "",
    sujet: params.get("sujet") ?? "",
  });
  if (!parsed.success) {
    return errorResponse(parsed.error.issues[0]?.message ?? "Requête invalide", 400);
  }
  try {
    return okResponse(await commentAVote(parsed.data.depute.toUpperCase(), parsed.data.sujet));
  } catch (error) {
    if (error instanceof CivixError && error.status === 404) {
      return errorResponse("Député introuvable.", 404);
    }
    return errorResponse("Données momentanément indisponibles.", 502);
  }
}
