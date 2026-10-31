import type { HomeView } from "@/lib/data/view-types";
import { LiveFigures } from "./live-figures";
import { GroupsSection } from "./groups-section";
import { Section } from "./section";
import { TrendsSection } from "./trends-section";
import { Unavailable } from "./unavailable";

export const LiveSection: React.FC<{ view: HomeView }> = ({ view }) => {
  const { week, trends, groupes } = view;
  const nothing = week === null && trends === null && groupes === null;
  return (
    <Section
      id="tendances"
      title="Les derniers chiffres de l'Assemblée"
      intro="Les mêmes données que celles que lit votre assistant, mises à jour automatiquement."
      tone="surface"
    >
      {nothing ? (
        <Unavailable />
      ) : (
        <div className="flex flex-col gap-14">
          <LiveFigures counters={view.counters} week={week} trends={trends} />
          {trends !== null ? <TrendsSection trends={trends} /> : null}
          {groupes !== null ? <GroupsSection groupes={groupes} /> : null}
        </div>
      )}
    </Section>
  );
};
