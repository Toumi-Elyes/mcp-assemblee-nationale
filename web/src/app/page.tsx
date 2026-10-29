import { Benefits } from "@/components/benefits";
import { CapabilitiesSection } from "@/components/capabilities-section";
import { DemoSection } from "@/components/demo-section";
import { FaqSection } from "@/components/faq-section";
import { FinalCta } from "@/components/final-cta";
import { GuaranteesSection } from "@/components/guarantees-section";
import { Hero } from "@/components/hero";
import { LiveProvider } from "@/components/live-context";
import { HowItWorks } from "@/components/how-it-works";
import { InstallSection } from "@/components/install-section";
import { LiveSection } from "@/components/live-section";
import { Problem } from "@/components/problem";
import { Tagline } from "@/components/tagline";
import { GITHUB_URL, MCP_URL, SITE_NAME, SITE_URL } from "@/lib/config";
import { getHomeView } from "@/lib/data/home-view";
import { isEmptyView, keepLastGoodVersion } from "@/lib/data/last-good";
import { buildLiveSnapshot } from "@/lib/data/live";
import { settle } from "@/lib/data/result";
import type { HomeView } from "@/lib/data/view-types";

export const revalidate = 1800;

const EMPTY_VIEW: HomeView = {
  generatedAt: new Date(),
  counters: { legislature: null, scrutins: null, latestDate: null, deputes: null, groupes: null },
  week: null,
  trends: null,
  groupes: null,
  suggestions: { topics: [], deputes: [] },
  heroChat: null,
};

function structuredData(): string {
  const data = [
    { "@context": "https://schema.org", "@type": "WebSite", name: SITE_NAME, url: SITE_URL, inLanguage: "fr" },
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      name: SITE_NAME,
      applicationCategory: "UtilitiesApplication",
      operatingSystem: "Web",
      isAccessibleForFree: true,
      offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" },
      license: "https://opensource.org/license/mit",
      codeRepository: GITHUB_URL,
      url: MCP_URL,
    },
  ];
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

const HomePage = async () => {
  const loaded = await settle(getHomeView());
  const view = loaded.ok ? loaded.data : EMPTY_VIEW;
  keepLastGoodVersion(!loaded.ok || isEmptyView(view));
  return (
    <main id="contenu">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: structuredData() }} />
      <LiveProvider initial={buildLiveSnapshot(view)}>
      <Hero chat={view.heroChat} generatedAt={view.generatedAt} />
      <Problem />
      <Benefits counters={view.counters} />
      <HowItWorks />
      <Tagline />
      <LiveSection view={view} />
      </LiveProvider>
      <DemoSection suggestions={view.suggestions} />
      <CapabilitiesSection />
      <InstallSection />
      <GuaranteesSection />
      <FaqSection />
      <FinalCta />
    </main>
  );
};

export default HomePage;
