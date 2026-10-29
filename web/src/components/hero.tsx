import { ChatExample } from "./chat-example";
import { HeroProof } from "./hero-proof";
import { InstallLine } from "./install-line";
import { WeekSection } from "./week-section";
import type { HeroChat } from "@/lib/data/view-types";

type HeroProps = { chat: HeroChat | null; generatedAt: Date };

export const Hero: React.FC<HeroProps> = ({ chat, generatedAt }) => {
  return (
    <>
      <section aria-labelledby="titre-principal" className="pb-6 pt-6 sm:pt-6">
        <div className="mx-auto flex w-full max-w-page flex-col gap-5 px-4 sm:px-6">
          <div className="grid gap-6 lg:grid-cols-12 lg:items-end lg:gap-8">
            <div className="flex flex-col gap-3 lg:col-span-8">
              <h1
                id="titre-principal"
                className="font-display text-4xl font-semibold leading-none tracking-tight sm:text-6xl lg:text-display"
              >
                <span className="lg:block lg:whitespace-nowrap">Sachez comment ont voté</span>{" "}
                <span className="lg:block lg:whitespace-nowrap">vos députés, source à l'appui</span>
              </h1>
              <p className="max-w-measure text-base text-ink-soft">
                Ajoutez un connecteur gratuit à votre assistant IA. Il va chercher les vrais scrutins de l'Assemblée
                nationale au lieu de répondre de mémoire, et il cite le lien de chacun.
              </p>
            </div>
            <div className="lg:col-span-4 lg:pb-1">
              <HeroProof />
            </div>
          </div>
          <InstallLine fieldId="adresse-connecteur" headingId="ajouter-titre" compact className="border-t-2 border-rule pt-4" />
        </div>
      </section>
      <div id="en-direct" className="pb-16 sm:pb-20">
        <div className="mx-auto grid w-full max-w-page gap-12 px-4 sm:px-6 lg:grid-cols-12">
          <div className="lg:col-span-8">
            <WeekSection />
          </div>
          <aside aria-label="Exemple de réponse" className="lg:col-span-4">
            <div className="lg:sticky lg:top-6">
              <ChatExample chat={chat} generatedAt={generatedAt} />
            </div>
          </aside>
        </div>
      </div>
    </>
  );
};
