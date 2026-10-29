import type { Groupe } from "@/lib/civix/types";
import { formatNumber, formatPercent } from "@/lib/format";
import { groupShares, totalSeats } from "@/lib/stats";
import { Section, Unavailable } from "./section";

const PALETTE = [
  "#3d5a9e",
  "#4f8a8b",
  "#a3763d",
  "#7a5c9e",
  "#5d8c4a",
  "#b05a6a",
  "#4a7fa3",
  "#8a7f3d",
  "#6b6f7a",
  "#a0623d",
  "#3d8a6e",
  "#7d6bb0",
];

export const GroupsSection: React.FC<{ groupes: Groupe[] | null }> = ({ groupes }) => {
  if (groupes === null || groupes.length === 0) {
    return (
      <Section id="groupes" eyebrow="Composition" title="Les groupes parlementaires">
        <Unavailable />
      </Section>
    );
  }
  const shares = groupShares(groupes);
  const total = totalSeats(groupes);
  const summary = `Répartition des ${formatNumber(total)} sièges entre ${groupes.length} groupes : ${shares
    .map((item) => `${item.groupe.abbr} ${item.groupe.size}`)
    .join(", ")}.`;

  return (
    <Section
      id="groupes"
      eyebrow="Composition"
      title="Les groupes parlementaires"
      intro={`${formatNumber(total)} députés répartis en ${groupes.length} groupes. Les couleurs servent seulement à distinguer les groupes entre eux.`}
    >
      <div className="card p-5">
        <div
          role="img"
          aria-label={summary}
          className="flex h-10 w-full overflow-hidden rounded-lg border border-line"
        >
          {shares.map((item, index) => (
            <div
              key={item.groupe.uid}
              title={`${item.groupe.abbr} : ${item.groupe.size}`}
              style={{ width: `${item.share * 100}%`, background: PALETTE[index % PALETTE.length] }}
            />
          ))}
        </div>
        <ul className="mt-5 grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-3">
          {shares.map((item, index) => (
            <li key={item.groupe.uid} className="flex items-start gap-3 text-sm">
              <span
                aria-hidden
                className="mt-1.5 size-3 shrink-0 rounded-sm"
                style={{ background: PALETTE[index % PALETTE.length] }}
              />
              <span className="min-w-0 flex-1">
                <span className="font-semibold">{item.groupe.abbr}</span>{" "}
                <span className="text-muted">{item.groupe.label}</span>
              </span>
              <span className="whitespace-nowrap tabular-nums">
                {formatNumber(item.groupe.size)}{" "}
                <span className="text-muted">({formatPercent(item.share)})</span>
              </span>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-xs text-muted">
          Source : liste des groupes et effectifs publiée par l&apos;Assemblée nationale via CIVIX. Les groupes sont
          classés par effectif.
        </p>
      </div>
    </Section>
  );
};
