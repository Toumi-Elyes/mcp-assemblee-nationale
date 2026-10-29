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
      title="Ce que le connecteur lit aujourd'hui"
      intro="Ces chiffres sont lus dans les données de l'Assemblée nationale, sans mise en forme à la main."
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
