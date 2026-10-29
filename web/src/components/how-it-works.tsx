import { INSTALL_HREF } from "@/lib/config";
import { LINK_TEXT } from "./button-styles";
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
    <Section split
      id="fonctionnement"
      eyebrow="Comment ça marche"
      title="Trois étapes, aucune ligne de code"
      intro="Un connecteur est une adresse que votre assistant sait interroger pour obtenir des données fiables. Son nom technique est MCP."
      tone="surface"
    >
      <ol className="flex flex-col gap-6">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <div className="h-full">
              <div className="flex gap-6 rounded-lg border border-line bg-raised p-6">
                <span className="tabular text-6xl font-bold text-accent">0{index + 1}</span>
                <div className="flex flex-col gap-2">
                  <h3 className="text-xl font-bold">{step.title}</h3>
                  <p className="text-base text-muted">{step.text}</p>
                </div>
              </div>
            </div>
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
