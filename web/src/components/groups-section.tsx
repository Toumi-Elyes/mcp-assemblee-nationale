import type { Groupe } from "@/lib/civix/types";
import { formatNumber } from "@/lib/format";
import { groupShares, totalSeats } from "@/lib/stats";
import { Hemicycle } from "./hemicycle";

export const GroupsSection: React.FC<{ groupes: readonly Groupe[] }> = ({ groupes }) => {
  const groups = groupShares(groupes).map(({ groupe }) => ({
    abbr: groupe.abbr,
    label: groupe.label,
    size: groupe.size,
  }));
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-2xl font-bold">Composition de l'Assemblée</h3>
        <p className="max-w-hero text-base text-muted">
          <span className="tabular font-bold text-ink">{formatNumber(totalSeats(groupes))}</span> députés
          répartis en {groupes.length} groupes, classés par effectif. Le classement ne dit rien d'autre que la taille.
        </p>
      </div>
      <Hemicycle groups={groups} />
    </div>
  );
};
