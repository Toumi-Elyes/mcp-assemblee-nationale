import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeftIcon } from "@phosphor-icons/react/dist/ssr";
import { LINK_TEXT } from "@/components/button-styles";
import { ChangelogList } from "@/components/changelog-list";
import { CHANGELOG } from "@/content/changelog";
import { GITHUB_URL } from "@/lib/config";

export const metadata: Metadata = {
  title: "Nouveautés",
  description: "Le journal daté des nouveautés, améliorations et corrections du connecteur MCP Assemblée nationale.",
  alternates: { canonical: "/nouveautes" },
};

const NouveautesPage: React.FC = () => {
  const changes = CHANGELOG.reduce((total, day) => total + day.changes.length, 0);
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-10 px-4 pb-24 pt-10 sm:px-6">
      <header className="flex max-w-3xl flex-col gap-5 border-b-2 border-rule pb-8">
        <Link href="/" className={`${LINK_TEXT} inline-flex items-center gap-2 text-sm font-bold`}>
          <ArrowLeftIcon aria-hidden="true" size={16} weight="bold" />
          Retour à l'accueil
        </Link>
        <h1 className="font-display text-5xl font-semibold tracking-tight sm:text-6xl">Nouveautés</h1>
        <p className="text-xl text-ink-soft">
          {changes} changements depuis le lancement, du plus récent au plus ancien. Chacun renvoie vers sa
          modification sur GitHub, où le même journal est publié dans{" "}
          <a href={`${GITHUB_URL}/blob/main/CHANGELOG.md`} className={LINK_TEXT}>
            CHANGELOG.md
          </a>
          .
        </p>
      </header>
      <ChangelogList days={CHANGELOG} headingLevel="h2" />
    </main>
  );
};

export default NouveautesPage;
