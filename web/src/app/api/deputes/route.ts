import { NextResponse, type NextRequest } from "next/server";
import { z } from "zod";
import { findDeputeCandidates } from "@/lib/data/demo";

const querySchema = z.object({ q: z.string().trim().min(2).max(100) });
const CACHE_CONTROL = "public, s-maxage=600, stale-while-revalidate=3600";

export async function GET(request: NextRequest) {
  const parsed = querySchema.safeParse({ q: request.nextUrl.searchParams.get("q") ?? "" });
  if (!parsed.success) {
    return NextResponse.json({ error: "Saisissez au moins 2 lettres." }, { status: 400 });
  }
  try {
    const deputes = await findDeputeCandidates(parsed.data.q);
    return NextResponse.json({ deputes }, { headers: { "Cache-Control": CACHE_CONTROL } });
  } catch {
    return NextResponse.json({ error: "Données momentanément indisponibles." }, { status: 502 });
  }
}
