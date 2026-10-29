import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { getHomeView } from "@/lib/data/home-view";
import { settle } from "@/lib/data/result";
import { formatDay, formatNumber } from "@/lib/format";
import { SITE_NAME } from "@/lib/config";

export const revalidate = 1800;
export const alt = "Comment ont voté vos députés ? Chiffres officiels et source de chaque scrutin.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const FONT_PATH = join(process.cwd(), "node_modules", "geist", "dist", "fonts", "geist-sans", "Geist-SemiBold.ttf");

async function loadFont(): Promise<ArrayBuffer | null> {
  try {
    const file = await readFile(FONT_PATH);
    return file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength) as ArrayBuffer;
  } catch {
    return null;
  }
}

export default async function OpenGraphImage() {
  const [loaded, font] = await Promise.all([settle(getHomeView()), loadFont()]);
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
          backgroundColor: "#131209",
          color: "#f4f4f1",
          fontFamily: font !== null ? "Geist" : "sans-serif",
        }}
      >
        <div style={{ display: "flex", fontSize: 32, color: "#a6a6a0", fontWeight: 600 }}>{SITE_NAME}</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={{ display: "flex", fontSize: 76, fontWeight: 600, lineHeight: 1.05 }}>
            Sachez comment ont voté vos députés, source à l'appui
          </div>
          <div style={{ display: "flex", fontSize: 32, color: "#a6a6a0" }}>{proof}</div>
        </div>
        <div style={{ display: "flex", fontSize: 28, color: "#93a6ff", fontWeight: 600 }}>
          Connecteur gratuit pour Claude et ChatGPT
        </div>
      </div>
    ),
    {
      ...size,
      fonts: font !== null ? [{ name: "Geist", data: font, weight: 600, style: "normal" }] : undefined,
    },
  );
}
