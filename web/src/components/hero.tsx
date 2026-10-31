import { ArrowDownIcon } from "@phosphor-icons/react/dist/ssr";
import { INSTALL_HREF } from "@/lib/config";
import type { HeroChat } from "@/lib/data/view-types";
import { LINK_TEXT } from "./button-styles";
import { ChatExample } from "./chat-example";
import { CopyField } from "./copy-field";

const Step: React.FC<{ index: number; title: string; children?: React.ReactNode }> = ({ index, title, children }) => {
  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-4">
      <span
        aria-hidden="true"
        className="grid size-7 shrink-0 place-items-center rounded-full border-2 border-rule font-display text-sm font-bold"
      >
        {index}
      </span>
      <div className="flex min-w-0 flex-col gap-2 pt-0.5">
        <p className="text-lg font-medium leading-snug">
          <span className="sr-only">Étape {index} : </span>
          {title}
        </p>
        {children}
      </div>
    </li>
  );
};

type HeroProps = { chat: HeroChat | null; generatedAt: Date };

export const Hero: React.FC<HeroProps> = ({ chat, generatedAt }) => {
  return (
    <section aria-labelledby="titre-principal" className="pb-16 pt-12 sm:pb-20 sm:pt-16">
      <div className="mx-auto grid w-full max-w-page gap-12 px-4 sm:px-6 lg:grid-cols-12 lg:gap-12">
        <div className="flex flex-col gap-10 lg:col-span-7">
          <div className="flex flex-col gap-5">
            <h1
              id="titre-principal"
              className="font-display text-4xl font-semibold leading-none tracking-tight sm:text-6xl"
            >
              <span className="lg:block">Demandez à votre assistant IA</span>{" "}
              <span className="lg:block">comment ont voté vos députés</span>
            </h1>
            <p className="max-w-measure text-lg text-ink-soft sm:text-xl">
              Claude ou ChatGPT vont chercher le vrai vote dans les données de l'Assemblée nationale, au lieu de répondre
              de mémoire, et vous donnent le lien pour vérifier. C'est gratuit.
            </p>
          </div>
          <div className="flex max-w-2xl flex-col gap-4">
            <h2 id="ajouter-titre" className="font-display text-2xl font-semibold tracking-tight">
              Comment ça marche
            </h2>
            <ol className="flex flex-col gap-5">
              <Step index={1} title="Copiez cette adresse.">
                <CopyField id="adresse-connecteur" />
              </Step>
              <Step index={2} title="Collez l'adresse dans les réglages de Claude, ou de ChatGPT en formule payante.">
                <a href={INSTALL_HREF} className={`${LINK_TEXT} self-start text-base font-medium`}>
                  Où la coller, étape par étape{" "}
                  <ArrowDownIcon aria-hidden="true" size={14} weight="bold" className="inline" />
                </a>
              </Step>
              <Step index={3} title="Activez le connecteur dans la conversation, puis posez votre question en français." />
            </ol>
            <p className="text-sm text-ink-soft">Gratuit, sans inscription, sans mot de passe.</p>
          </div>
        </div>
        <aside aria-label="Exemple de réponse" className="lg:col-span-5">
          <ChatExample chat={chat} generatedAt={generatedAt} />
        </aside>
      </div>
    </section>
  );
};
