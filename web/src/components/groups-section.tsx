import type { Groupe } from "@/lib/civix/types";
import { formatNumber } from "@/lib/format";
import { groupShares, totalSeats } from "@/lib/stats";
import { SeatGrid } from "./seat-grid";
import { Plate } from "./plate";

export const GroupsSection: React.FC<{ groupes: readonly Groupe[] }> = ({ groupes }) => {
  const groups = groupShares(groupes).map(({ groupe }) => ({
    abbr: groupe.abbr,
    label: groupe.label,
    size: groupe.size,
  }));
  return (
    <Plate
      number={5}
      title="Composition de l'Assemblée"
      note={`${formatNumber(totalSeats(groupes))} députés répartis en ${groupes.length} groupes, classés par effectif. Le classement ne dit rien d'autre que la taille.`}
    >
      <SeatGrid groups={groups} />
    </Plate>
  );
};
