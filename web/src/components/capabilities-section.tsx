import { CAPABILITIES, READY_PROMPTS } from "@/content/capabilities";
import { Reveal } from "./reveal";
import { Section } from "./section";

export const CapabilitiesSection: React.FC = () => {
  return (
    <Section
      id="possibilites"
      eyebrow="Ce que le connecteur sait faire"
      title="Douze outils, des questions simples"
      intro="Vous n'avez pas besoin de connaître leur nom : posez la question, l'assistant choisit l'outil. Tous sont en lecture seule, il ne peut rien modifier."
      tone="surface"
    >
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {CAPABILITIES.map((item, index) => (
          <li key={item.tool}>
            <Reveal delay={(index % 3) * 80} className="h-full">
              <article className="flex h-full flex-col gap-2 rounded-2xl border border-line bg-raised p-6">
                <p className="text-lg font-semibold">« {item.question} »</p>
                <p className="text-sm text-muted">{item.detail}</p>
                <p className="mt-auto pt-2 text-xs text-muted">
                  Outil <code className="font-mono text-ink">{item.tool}</code>
                </p>
              </article>
            </Reveal>
          </li>
        ))}
      </ul>

      <div className="mt-16 flex flex-col gap-6">
        <div className="flex max-w-hero flex-col gap-2">
          <h3 className="text-2xl font-semibold">Trois demandes prêtes à l'emploi</h3>
          <p className="text-base text-muted">
            Le connecteur propose aussi des modèles de demande, accessibles depuis le menu des prompts de votre assistant.
          </p>
        </div>
        <ul className="grid gap-3 md:grid-cols-3">
          {READY_PROMPTS.map((prompt) => (
            <li key={prompt.name} className="flex flex-col gap-2 rounded-2xl border border-line bg-raised p-6">
              <p className="text-lg font-semibold">{prompt.label}</p>
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
