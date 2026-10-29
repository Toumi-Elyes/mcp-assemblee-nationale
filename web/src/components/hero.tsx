import { ArrowDownIcon } from "@phosphor-icons/react/dist/ssr";
import { INSTALL_HREF } from "@/lib/config";
import type { HeroChat } from "@/lib/data/view-types";
import { LINK_TEXT } from "./button-styles";
import { ChatExample } from "./chat-example";
import { CopyField } from "./copy-field";
import { HeroProof } from "./hero-proof";
import { VideoSection } from "./video-section";
import { WeekSection } from "./week-section";

type HeroProps = { chat: HeroChat | null; generatedAt: Date };

export const Hero: React.FC<HeroProps> = ({ chat, generatedAt }) => {
  return (
    <>
      <section aria-labelledby="titre-principal" className="pb-16 pt-12 sm:pb-20 sm:pt-16">
        <div className="mx-auto grid w-full max-w-page gap-12 px-4 sm:px-6 lg:grid-cols-12 lg:items-end lg:gap-8">
          <div className="flex flex-col gap-8 lg:col-span-8">
            <div className="flex flex-col gap-5">
              <h1
                id="titre-principal"
                className="font-display text-4xl font-semibold leading-none tracking-tight sm:text-6xl lg:text-display"
              >
                <span className="lg:block lg:whitespace-nowrap">Sachez comment ont voté</span>{" "}
                <span className="lg:block lg:whitespace-nowrap">vos députés, source à l'appui</span>
              </h1>
              <p className="max-w-measure text-lg text-ink-soft sm:text-xl">
                Un connecteur gratuit pour votre assistant IA : il consulte les vrais scrutins de l'Assemblée nationale
                et donne le lien de chacun.
              </p>
            </div>
            <div className="flex max-w-2xl flex-col gap-3">
              <h2 id="ajouter-titre" className="sr-only">
                Ajouter le connecteur à mon assistant
              </h2>
              <CopyField id="adresse-connecteur" />
              <p className="flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm text-ink-soft">
                <span>Gratuit, sans compte, sans clé.</span>
                <a href={INSTALL_HREF} className={`${LINK_TEXT} font-medium`}>
                  Où coller l'adresse, assistant par assistant{" "}
                  <ArrowDownIcon aria-hidden="true" size={14} weight="bold" className="inline" />
                </a>
              </p>
            </div>
          </div>
          <div className="lg:col-span-4 lg:pb-2">
            <HeroProof />
          </div>
        </div>
      </section>
      <VideoSection />
      <div id="en-direct" className="border-t-2 border-rule pb-20 pt-14 sm:pb-24">
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
