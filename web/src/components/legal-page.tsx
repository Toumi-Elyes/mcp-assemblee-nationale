import Link from "next/link";
import { ArrowLeftIcon } from "@phosphor-icons/react/dist/ssr";
import { LINK_TEXT } from "./button-styles";

type LegalBlock = { title: string; paragraphs: readonly React.ReactNode[] };

type LegalPageProps = { title: string; intro: string; blocks: readonly LegalBlock[] };

export const LegalPage: React.FC<LegalPageProps> = ({ title, intro, blocks }) => {
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col gap-10 px-4 pb-24 pt-12 sm:px-6">
      <header className="flex max-w-hero flex-col gap-4">
        <Link href="/" className={`${LINK_TEXT} inline-flex items-center gap-2 text-sm font-bold`}>
          <ArrowLeftIcon aria-hidden="true" size={16} weight="bold" />
          Retour à l'accueil
        </Link>
        <h1 className="font-serif text-5xl font-bold">{title}</h1>
        <p className="text-lg text-muted">{intro}</p>
      </header>
      <div className="flex max-w-hero flex-col gap-8">
        {blocks.map((block) => (
          <section key={block.title} className="flex flex-col gap-3">
            <h2 className="text-2xl font-bold">{block.title}</h2>
            {block.paragraphs.map((paragraph, index) => (
              <p key={index} className="text-base text-muted">
                {paragraph}
              </p>
            ))}
          </section>
        ))}
      </div>
    </main>
  );
};
