import Link from "next/link";
import { ArrowLeftIcon } from "@phosphor-icons/react/dist/ssr";
import { LINK_TEXT } from "./button-styles";

type LegalBlock = { title: string; paragraphs: readonly React.ReactNode[] };

type LegalPageProps = { title: string; intro: string; blocks: readonly LegalBlock[] };

export const LegalPage: React.FC<LegalPageProps> = ({ title, intro, blocks }) => {
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-10 px-4 pb-24 pt-10 sm:px-6">
      <header className="flex max-w-3xl flex-col gap-5 border-b-2 border-rule pb-8">
        <Link href="/" className={`${LINK_TEXT} inline-flex items-center gap-2 text-sm font-bold`}>
          <ArrowLeftIcon aria-hidden="true" size={16} weight="bold" />
          Retour à l'accueil
        </Link>
        <h1 className="font-display text-5xl font-semibold tracking-tight sm:text-6xl">{title}</h1>
        <p className="text-xl text-ink-soft">{intro}</p>
      </header>
      <div className="flex max-w-measure flex-col gap-10">
        {blocks.map((block) => (
          <section key={block.title} className="flex flex-col gap-3">
            <h2 className="font-display text-2xl font-semibold tracking-tight">{block.title}</h2>
            {block.paragraphs.map((paragraph, index) => (
              <p key={index} className="text-base leading-relaxed text-ink-soft">
                {paragraph}
              </p>
            ))}
          </section>
        ))}
      </div>
    </main>
  );
};
