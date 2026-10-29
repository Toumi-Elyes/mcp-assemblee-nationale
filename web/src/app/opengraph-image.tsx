import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { getHomeView } from "@/lib/data/home-view";
import { isEmptyView, keepLastGoodVersion } from "@/lib/data/last-good";
import { settle } from "@/lib/data/result";
import { formatDay, formatNumber } from "@/lib/format";
import { SITE_NAME } from "@/lib/config";

export const revalidate = 1800;
export const alt = "Comment ont voté vos députés ? Chiffres officiels et source de chaque scrutin.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const FONT_PATH = join(process.cwd(), "node_modules", "@fontsource", "public-sans", "files", "public-sans-latin-700-normal.woff");
const DISPLAY_FONT_PATH = join(
  process.cwd(),
  "node_modules",
  "@fontsource",
  "barlow-semi-condensed",
  "files",
  "barlow-semi-condensed-latin-600-normal.woff",
);

async function loadFont(path: string): Promise<ArrayBuffer | null> {
  try {
    const file = await readFile(path);
    return file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength) as ArrayBuffer;
  } catch {
    return null;
  }
}

export default async function OpenGraphImage() {
  const [loaded, font, displayFont] = await Promise.all([
    settle(getHomeView()),
    loadFont(FONT_PATH),
    loadFont(DISPLAY_FONT_PATH),
  ]);
  keepLastGoodVersion(!loaded.ok || isEmptyView(loaded.data));
  const counters = loaded.ok ? loaded.data.counters : null;
  const proof =
    counters !== null && counters.scrutins !== null && counters.latestDate !== null
      ? `${formatNumber(counters.scrutins)} scrutins sous la ${counters.legislature ?? 17}e législature, dernier vote le ${formatDay(counters.latestDate)}`
      : "Données de l'Assemblée nationale lues en direct";
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          backgroundColor: "#ffffff",
          color: "#161616",
          fontFamily: font !== null ? "Public Sans" : "sans-serif",
        }}
      >
        <div style={{ display: "flex", fontSize: 32, color: "#666666", fontWeight: 700 }}>{SITE_NAME}</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div
            style={{
              display: "flex",
              fontSize: 92,
              fontWeight: 600,
              lineHeight: 0.98,
              letterSpacing: -1.5,
              fontFamily: displayFont !== null ? "Barlow Semi Condensed" : undefined,
            }}
          >
            Sachez comment ont voté vos députés, source à l'appui
          </div>
          <div style={{ display: "flex", fontSize: 32, color: "#666666" }}>{proof}</div>
        </div>
        <div style={{ display: "flex", fontSize: 28, color: "#000091", fontWeight: 700 }}>
          Connecteur gratuit pour Claude et ChatGPT
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        ...(font !== null ? [{ name: "Public Sans", data: font, weight: 700 as const, style: "normal" as const }] : []),
        ...(displayFont !== null
          ? [{ name: "Barlow Semi Condensed", data: displayFont, weight: 600 as const, style: "normal" as const }]
          : []),
      ],
    },
  );
}
