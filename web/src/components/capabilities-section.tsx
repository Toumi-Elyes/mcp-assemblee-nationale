import { CaretDownIcon, ChartLineUpIcon, ScalesIcon } from "@phosphor-icons/react/dist/ssr";
import {
  CAPABILITY_GROUPS,
  CHATGPT_COMPATIBILITY,
  READY_PROMPTS,
  TOOL_COUNT,
  type Capability,
} from "@/content/capabilities";
import { Section } from "./section";

const CapabilityCard: React.FC<{ item: Capability }> = ({ item }) => {
  return (
    <li>
      <article className="flex h-full flex-col gap-2 rounded-lg border border-line bg-raised p-6">
        <p className="text-lg font-bold">« {item.question} »</p>
        <p className="text-sm text-muted">{item.detail}</p>
        <p className="mt-auto pt-2 text-xs text-muted">
          Outil <code className="font-mono text-ink">{item.tool}</code>
        </p>
      </article>
    </li>
  );
};

export const CapabilitiesSection: React.FC = () => {
  return (
    <Section
      id="possibilites"
      eyebrow="Ce que le connecteur sait faire"
      title={`${TOOL_COUNT} outils, des questions simples`}
      intro="Vous n'avez pas besoin de connaître leur nom : posez la question, l'assistant choisit l'outil. Tous sont en lecture seule, il ne peut rien modifier."
      tone="surface"
    >
      <div className="mb-10 grid gap-4 md:grid-cols-2">
        <div className="flex gap-3 rounded-lg border border-line bg-raised p-6">
          <ChartLineUpIcon aria-hidden="true" size={32} weight="bold" className="shrink-0 text-accent" />
          <p className="text-base">
            <span className="font-bold">Chaque analyse se termine par un bloc « Méthode »</span> : période, taille de
            l'échantillon, définitions et limites. Vous voyez ce qui a été compté.
          </p>
        </div>
        <div className="flex gap-3 rounded-lg border border-line bg-raised p-6">
          <ScalesIcon aria-hidden="true" size={32} weight="bold" className="shrink-0 text-accent" />
          <p className="text-base">
            <span className="font-bold">Aucun classement de députés ni de groupes.</span> Les analyses décrivent les
            données, sans note, sans palmarès et sans interprétation politique.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {CAPABILITY_GROUPS.map((group, index) => (
          <details key={group.id} open={index < 2} className="group rounded-lg border border-line bg-bg">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-6">
              <span className="flex flex-col gap-1">
                <span className="font-serif text-2xl font-bold">{group.title}</span>
                <span className="text-sm text-muted">{group.intro}</span>
              </span>
              <span className="flex shrink-0 items-center gap-3">
                <span className="tabular text-sm font-bold text-accent">{group.items.length} outils</span>
                <CaretDownIcon aria-hidden="true" size={20} weight="bold" className="group-open:rotate-180" />
              </span>
            </summary>
            <ul className="grid gap-3 px-6 pb-6 sm:grid-cols-2 lg:grid-cols-3">
              {group.items.map((item) => (
                <CapabilityCard key={item.tool} item={item} />
              ))}
            </ul>
          </details>
        ))}
      </div>

      <div className="mt-10 flex flex-col gap-4">
        <div className="flex max-w-hero flex-col gap-2">
          <h3 className="font-serif text-2xl font-bold">Compatibilité recherche approfondie de ChatGPT</h3>
          <p className="text-base text-muted">
            Deux outils reprennent les mêmes données au format qu'attend ChatGPT pour sa recherche approfondie.
          </p>
        </div>
        <ul className="grid gap-3 sm:grid-cols-2">
          {CHATGPT_COMPATIBILITY.map((item) => (
            <CapabilityCard key={item.tool} item={item} />
          ))}
        </ul>
      </div>

      <div className="mt-16 flex flex-col gap-6">
        <div className="flex max-w-hero flex-col gap-2">
          <h3 className="font-serif text-2xl font-bold">{READY_PROMPTS.length} demandes prêtes à l'emploi</h3>
          <p className="text-base text-muted">
            Le connecteur propose aussi des modèles de demande, accessibles depuis le menu des prompts de votre assistant.
          </p>
        </div>
        <ul className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {READY_PROMPTS.map((prompt) => (
            <li key={prompt.name} className="flex flex-col gap-2 rounded-lg border border-line bg-raised p-6">
              <p className="text-lg font-bold">{prompt.label}</p>
              <p className="text-base">{prompt.example}</p>
              <p className="text-sm text-muted">{prompt.detail}</p>
              <p className="mt-auto pt-2 text-xs text-muted">
                Modèle <code className="font-mono text-ink">{prompt.name}</code>
              </p>
            </li>
          ))}
        </ul>
      </div>
    </Section>
  );
};
