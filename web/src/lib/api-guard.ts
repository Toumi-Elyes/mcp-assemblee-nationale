import { NextResponse, type NextRequest } from "next/server";

const SUCCESS_CACHE = "public, s-maxage=600, stale-while-revalidate=3600";
const ERROR_CACHE = "public, s-maxage=300";

export function rejectCrossSite(request: NextRequest): NextResponse | null {
  if (request.headers.get("sec-fetch-site") !== "cross-site") {
    return null;
  }
  return NextResponse.json(
    { error: "Origine non autorisée." },
    { status: 403, headers: { "Cache-Control": "no-store" } },
  );
}

export function okResponse(body: unknown, cacheControl: string = SUCCESS_CACHE): NextResponse {
  return NextResponse.json(body, { headers: { "Cache-Control": cacheControl } });
}

export function errorResponse(message: string, status: number): NextResponse {
  const cacheable = status === 400 || status === 404;
  return NextResponse.json(
    { error: message },
    { status, headers: cacheable ? { "Cache-Control": ERROR_CACHE } : { "Cache-Control": "no-store" } },
  );
}
