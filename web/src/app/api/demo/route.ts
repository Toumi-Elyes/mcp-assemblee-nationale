import { NextResponse, type NextRequest } from "next/server";
import { z } from "zod";
import { CivixError } from "@/lib/civix";
import { commentAVote } from "@/lib/data/demo";

const querySchema = z.object({
  depute: z.string().regex(/^PA\d{3,12}$/i, "Identifiant de député invalide"),
  sujet: z.string().trim().min(2, "Indiquez un sujet").max(200),
});
const CACHE_CONTROL = "public, s-maxage=600, stale-while-revalidate=3600";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const parsed = querySchema.safeParse({
    depute: params.get("depute") ?? "",
    sujet: params.get("sujet") ?? "",
  });
  if (!parsed.success) {
    const message = parsed.error.issues[0]?.message ?? "Requête invalide";
    return NextResponse.json({ error: message }, { status: 400 });
  }
  try {
    const answer = await commentAVote(parsed.data.depute.toUpperCase(), parsed.data.sujet);
    return NextResponse.json(answer, { headers: { "Cache-Control": CACHE_CONTROL } });
  } catch (error) {
    if (error instanceof CivixError && error.status === 404) {
      return NextResponse.json({ error: "Député introuvable." }, { status: 404 });
    }
    return NextResponse.json({ error: "Données momentanément indisponibles." }, { status: 502 });
  }
}
