import type { Groupe } from "@/lib/civix/types";
import { formatNumber, formatPercent } from "@/lib/format";
import { groupShares, totalSeats } from "@/lib/stats";
import { LINK_TEXT } from "./button-styles";

export const GroupsSection: React.FC<{ groupes: readonly Groupe[] }> = ({ groupes }) => {
  const shares = groupShares(groupes);
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-2xl font-semibold">Composition de l'Assemblée</h3>
        <p className="max-w-hero text-base text-muted">
          <span className="tabular font-mono font-semibold text-ink">{formatNumber(totalSeats(groupes))}</span> députés
          répartis en {groupes.length} groupes, classés par effectif.
        </p>
      </div>
      <ul className="grid gap-3 rounded-2xl border border-line bg-raised p-6 sm:grid-cols-2">
        {shares.map(({ groupe, share }) => (
          <li key={groupe.uid} className="flex flex-col gap-1">
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-sm">
                {groupe.url !== null ? (
                  <a href={groupe.url} className={`${LINK_TEXT} font-semibold`}>
                    {groupe.abbr}
                  </a>
                ) : (
                  <span className="font-semibold">{groupe.abbr}</span>
                )}{" "}
                <span className="text-muted">{groupe.label}</span>
              </span>
              <span className="tabular font-mono text-sm">{formatNumber(groupe.size)}</span>
            </div>
            <svg role="img" aria-label={`${formatPercent(share)} des sièges`} className="h-2 w-full overflow-hidden rounded-sm" preserveAspectRatio="none">
              <rect width="100%" height="100%" className="fill-absent" />
              <rect width={`${share * 100}%`} height="100%" className="fill-abstention" />
            </svg>
          </li>
        ))}
      </ul>
    </div>
  );
};
