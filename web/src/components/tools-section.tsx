import { PROMPTS, TOOLS } from "@/content/tools";
import { Section } from "./section";

export const ToolsSection: React.FC = () => {
  return (
    <Section
      id="outils"
      eyebrow="Ce que le MCP sait faire"
      title="12 outils, en lecture seule"
      intro="Vous posez la question en français, l'IA choisit l'outil. Rien n'est modifiable : le connecteur ne fait que lire des données publiques."
    >
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {TOOLS.map((tool) => (
          <li key={tool.name} className="card flex flex-col p-4">
            <code className="font-mono text-sm font-semibold text-accent">{tool.name}</code>
            <p className="mt-0.5 font-mono text-xs text-muted">({tool.params})</p>
            <p className="mt-2 text-sm">{tool.does}</p>
            <p className="mt-auto pt-3 text-sm italic text-muted">« {tool.example} »</p>
          </li>
        ))}
      </ul>

      <h3 className="mt-10 text-xl font-semibold">3 questions prêtes à l&apos;emploi</h3>
      <p className="mt-1 text-sm text-muted">Dans Claude, elles apparaissent dans le menu des prompts du connecteur.</p>
      <ul className="mt-4 grid gap-3 md:grid-cols-3">
        {PROMPTS.map((prompt) => (
          <li key={prompt.name} className="card p-4">
            <code className="font-mono text-sm font-semibold text-accent">{prompt.name}</code>
            <p className="mt-0.5 font-mono text-xs text-muted">({prompt.param})</p>
            <p className="mt-2 text-sm">{prompt.does}</p>
            <p className="mt-3 text-sm italic text-muted">« {prompt.example} »</p>
          </li>
        ))}
      </ul>
    </Section>
  );
};
