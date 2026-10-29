import { ImageResponse } from "next/og";
import { getHomeView } from "@/lib/data/home-view";
import { formatDay, formatNumber } from "@/lib/format";

export const revalidate = 1800;
export const alt = "MCP Assemblée nationale";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const Image = async () => {
  const { counters } = await getHomeView();
  const facts: { value: string; label: string }[] = [];
  if (counters.scrutins !== null) {
    facts.push({ value: formatNumber(counters.scrutins), label: "scrutins publiés" });
  }
  if (counters.latestDate !== null) {
    facts.push({ value: formatDay(counters.latestDate), label: "dernier vote" });
  }
  if (counters.deputes !== null) {
    facts.push({ value: formatNumber(counters.deputes), label: "députés" });
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#fbfaf7",
          color: "#16202e",
          padding: 72,
          fontFamily: "serif",
        }}
      >
        <div style={{ display: "flex", fontSize: 30, color: "#1f3f8f", fontWeight: 700 }}>
          MCP Assemblée nationale
        </div>
        <div style={{ display: "flex", fontSize: 76, lineHeight: 1.08, fontWeight: 700 }}>
          Demandez à votre IA comment votent vos députés
        </div>
        <div style={{ display: "flex", gap: 56 }}>
          {facts.map((fact) => (
            <div key={fact.label} style={{ display: "flex", flexDirection: "column" }}>
              <div style={{ fontSize: 48, fontWeight: 700 }}>{fact.value}</div>
              <div style={{ fontSize: 24, color: "#566170" }}>{fact.label}</div>
            </div>
          ))}
        </div>
      </div>
    ),
    size,
  );
};

export default Image;
