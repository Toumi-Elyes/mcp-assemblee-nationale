import { formatTimestamp } from "@/lib/format";
import type { HomeView } from "@/lib/data/view-types";
import { GroupsSection } from "./groups-section";
import { Section } from "./section";
import { TrendsSection } from "./trends-section";
import { Unavailable } from "./unavailable";
import { WeekSection } from "./week-section";

export const LiveSection: React.FC<{ view: HomeView }> = ({ view }) => {
  const { week, trends, groupes, generatedAt } = view;
  const nothing = week === null && trends === null && groupes === null;
  return (
    <Section
      id="en-direct"
      eyebrow="La preuve, en direct"
      title="Ce que le connecteur lit aujourd'hui"
      intro={`Ces chiffres sont lus dans les données de l'Assemblée nationale, sans mise en forme à la main. Dernière lecture : ${formatTimestamp(generatedAt)}.`}
      tone="surface"
    >
      {nothing ? (
        <Unavailable />
      ) : (
        <div className="flex flex-col gap-16">
          {week !== null ? <WeekSection week={week} /> : null}
          {trends !== null ? <TrendsSection trends={trends} /> : null}
          {groupes !== null ? <GroupsSection groupes={groupes} /> : null}
        </div>
      )}
    </Section>
  );
};
