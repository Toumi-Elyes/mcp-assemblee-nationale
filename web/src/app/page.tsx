import { DemoSection } from "@/components/demo-section";
import { GroupsSection } from "@/components/groups-section";
import { Hero } from "@/components/hero";
import { InstallSection } from "@/components/install-section";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { ToolsSection } from "@/components/tools-section";
import { TrendsSection } from "@/components/trends-section";
import { WeekSection } from "@/components/week-section";
import { getHomeView } from "@/lib/data/home-view";

export const revalidate = 1800;

const HomePage = async () => {
  const view = await getHomeView();
  return (
    <>
      <SiteHeader />
      <main id="contenu">
        <Hero counters={view.counters} />
        <WeekSection week={view.week} />
        <TrendsSection trends={view.trends} />
        <GroupsSection groupes={view.groupes} />
        <DemoSection topics={view.suggestions.topics} deputes={view.suggestions.deputes} />
        <ToolsSection />
        <InstallSection />
      </main>
      <SiteFooter updatedAt={view.generatedAt} />
    </>
  );
};

export default HomePage;
