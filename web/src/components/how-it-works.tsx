import { INSTALL_HREF } from "@/lib/config";
import { LINK_TEXT } from "./button-styles";
import { Reveal } from "./reveal";
import { Section } from "./section";

const STEPS = [
  {
    title: "Copiez l'adresse",
    text: "Un bouton la copie pour vous. C'est l'adresse du connecteur, rien d'autre.",
  },
  {
    title: "Collez l'adresse dans votre assistant",
    text: "Dans les réglages des connecteurs de Claude ou de ChatGPT, ajoutez un connecteur personnalisé.",
  },
  {
    title: "Posez votre question",
    text: "En français, comme à une personne : « Comment a voté ma députée sur le budget ? »",
  },
] as const;

export const HowItWorks: React.FC = () => {
  return (
    <Section
      id="fonctionnement"
      eyebrow="Comment ça marche"
      title="Trois étapes, aucune ligne de code"
      intro="Un connecteur est une adresse que votre assistant sait interroger pour obtenir des données fiables. Son nom technique est MCP."
      tone="surface"
    >
      <ol className="grid gap-6 md:grid-cols-3">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <Reveal delay={index * 100} className="h-full">
              <div className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-raised p-6">
                <span className="tabular font-mono text-4xl font-semibold text-muted">0{index + 1}</span>
                <h3 className="text-xl font-semibold">{step.title}</h3>
                <p className="text-base text-muted">{step.text}</p>
              </div>
            </Reveal>
          </li>
        ))}
      </ol>
      <p className="mt-8 text-base">
        <a href={INSTALL_HREF} className={LINK_TEXT}>
          Voir les étapes détaillées pour chaque assistant
        </a>
      </p>
    </Section>
  );
};
