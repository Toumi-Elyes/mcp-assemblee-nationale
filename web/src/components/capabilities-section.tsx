import { CaretDownIcon } from "@phosphor-icons/react/dist/ssr";
import {
  CAPABILITY_GROUPS,
  CHATGPT_COMPATIBILITY,
  READY_PROMPTS,
  TOOL_COUNT,
  type Capability,
} from "@/content/capabilities";
import { Section } from "./section";

function frenchSpacing(text: string): string {
  return text.replace(/ ([?!:;»])/g, "\u00a0$1").replace(/« /g, "«\u00a0");
}

const ROW = "grid gap-x-8 gap-y-1 border-b border-line py-4 md:grid-cols-[minmax(0,5fr)_minmax(0,5fr)_minmax(0,2fr)]";

const CapabilityRow: React.FC<{ item: Capability }> = ({ item }) => {
  return (
    <li className={ROW}>
      <p className="text-lg font-medium leading-snug">«&nbsp;{frenchSpacing(item.question)}&nbsp;»</p>
      <p className="text-sm text-ink-soft">{item.detail}</p>
      <p className="text-xs text-muted md:text-right">
        <span className="sr-only">Outil </span>
        <code className="font-mono text-ink">{item.tool}</code>
      </p>
    </li>
  );
};

const Principle: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  return (
    <div className="flex flex-col gap-1 border-t border-rule pt-4">
      <p className="font-display text-xl font-semibold leading-tight">{title}</p>
      <p className="text-base text-ink-soft">{children}</p>
    </div>
  );
};

export const CapabilitiesSection: React.FC = () => {
  return (
    <Section
      id="possibilites"
      title={`${TOOL_COUNT} outils, des questions simples`}
      intro="Vous n'avez pas besoin de connaître leur nom : posez la question, l'assistant choisit l'outil. Tous sont en lecture seule, il ne peut rien modifier."
    >
      <div className="mb-12 grid gap-8 md:grid-cols-2">
        <Principle title="Chaque analyse se termine par un bloc «&nbsp;Méthode&nbsp;»">
          Période, taille de l'échantillon, définitions et limites. Vous voyez ce qui a été compté.
        </Principle>
        <Principle title="Aucun classement de députés ni de groupes">
          Les analyses décrivent les données, sans note, sans palmarès et sans interprétation politique.
        </Principle>
      </div>

      <div className="flex flex-col gap-2">
        <div
          aria-hidden="true"
          className="hidden border-b-2 border-rule pb-2 font-display text-sm font-semibold uppercase tracking-wide text-muted md:grid md:grid-cols-[minmax(0,5fr)_minmax(0,5fr)_minmax(0,2fr)] md:gap-x-8"
        >
          <span>Vous demandez</span>
          <span>Le connecteur</span>
          <span className="text-right">Outil</span>
        </div>
        {CAPABILITY_GROUPS.map((group, index) => (
          <details key={group.id} open={index === 0} className="group">
            <summary className="flex cursor-pointer list-none items-baseline justify-between gap-4 border-b border-rule py-4 transition-colors hover:text-accent">
              <span className="flex flex-col gap-1">
                <span className="font-display text-2xl font-semibold tracking-tight">{group.title}</span>
                <span className="text-sm text-ink-soft">{group.intro}</span>
              </span>
              <span className="flex shrink-0 items-center gap-3">
                <span className="tabular font-display text-base font-semibold">{group.items.length} outils</span>
                <CaretDownIcon aria-hidden="true" size={20} weight="bold" className="transition-transform group-open:rotate-180" />
              </span>
            </summary>
            <ul className="mb-6">
              {group.items.map((item) => (
                <CapabilityRow key={item.tool} item={item} />
              ))}
            </ul>
          </details>
        ))}
      </div>

      <div className="mt-14 grid gap-8 lg:grid-cols-12">
        <div className="flex flex-col gap-2 lg:col-span-4">
          <h3 className="font-display text-2xl font-semibold tracking-tight">Compatibilité recherche approfondie de ChatGPT</h3>
          <p className="text-base text-ink-soft">
            Deux outils reprennent les mêmes données au format qu'attend ChatGPT pour sa recherche approfondie.
          </p>
        </div>
        <ul className="border-t-2 border-rule lg:col-span-8">
          {CHATGPT_COMPATIBILITY.map((item) => (
            <CapabilityRow key={item.tool} item={item} />
          ))}
        </ul>
      </div>

      <div className="mt-14 grid gap-8 lg:grid-cols-12">
        <div className="flex flex-col gap-2 lg:col-span-4">
          <h3 className="font-display text-2xl font-semibold tracking-tight">
            {READY_PROMPTS.length} demandes prêtes à l'emploi
          </h3>
          <p className="text-base text-ink-soft">
            Le connecteur propose aussi des modèles de demande, accessibles depuis le menu des prompts de votre assistant.
          </p>
        </div>
        <ul className="grid border-t-2 border-rule sm:grid-cols-2 sm:gap-x-8 lg:col-span-8">
          {READY_PROMPTS.map((prompt) => (
            <li key={prompt.name} className="flex flex-col gap-1.5 border-b border-line py-4">
              <p className="flex items-baseline justify-between gap-3">
                <span className="font-display text-xl font-semibold leading-tight">{prompt.label}</span>
                <span className="text-xs text-muted">
                  <span className="sr-only">Modèle </span>
                  <code className="font-mono">{prompt.name}</code>
                </span>
              </p>
              <p className="text-base">{prompt.example}</p>
              <p className="text-sm text-ink-soft">{prompt.detail}</p>
            </li>
          ))}
        </ul>
      </div>
    </Section>
  );
};
