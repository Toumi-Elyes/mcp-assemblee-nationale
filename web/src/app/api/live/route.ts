import type { NextRequest } from "next/server";
import { errorResponse, okResponse, rejectCrossSite } from "@/lib/api-guard";
import { getHomeView } from "@/lib/data/home-view";
import { buildLiveSnapshot } from "@/lib/data/live";
import { isEmptyView } from "@/lib/data/last-good";
import { settle } from "@/lib/data/result";

const LIVE_CACHE = "public, s-maxage=120, stale-while-revalidate=600";

export async function GET(request: NextRequest) {
  const blocked = rejectCrossSite(request);
  if (blocked !== null) {
    return blocked;
  }
  const loaded = await settle(getHomeView());
  if (!loaded.ok || isEmptyView(loaded.data)) {
    return errorResponse("Données momentanément indisponibles.", 502);
  }
  return okResponse(buildLiveSnapshot(loaded.data), LIVE_CACHE);
}
