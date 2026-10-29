import { CheckCircleIcon, WarningCircleIcon } from "@phosphor-icons/react/dist/ssr";
import { Section } from "./section";

type Side = { title: string; text: string; points: readonly string[]; Icon: typeof WarningCircleIcon };

const SIDES: readonly Side[] = [
  {
    title: "Un assistant seul",
    text: "Il répond de mémoire.",
    points: [
      "Les chiffres peuvent être anciens ou approximatifs.",
      "Aucun lien ne permet de vérifier le vote cité.",
      "Un même texte compte plusieurs scrutins, et il est facile de les confondre.",
    ],
    Icon: WarningCircleIcon,
  },
  {
    title: "Avec le connecteur",
    text: "Il va chercher le vote.",
    points: [
      "Les décomptes viennent des données ouvertes de l'Assemblée.",
      "Le détail par groupe et par député est lu au moment de la question.",
      "Chaque réponse cite la page du scrutin à ouvrir.",
    ],
    Icon: CheckCircleIcon,
  },
];

export const Problem: React.FC = () => {
  return (
    <Section split
      id="pourquoi"
      eyebrow="Le problème"
      title="Vérifier un vote prend une heure. Se fier à une réponse de mémoire, c'est risqué."
      intro="Savoir comment un député a voté oblige à fouiller assemblee-nationale.fr, scrutin par scrutin. Et un assistant IA, seul, peut répondre avec aplomb sans avoir les bons chiffres."
      tone="surface"
    >
      <div className="grid gap-6 md:grid-cols-2">
        {SIDES.map((side) => (
          <div key={side.title}>
            <article className="flex h-full flex-col gap-4 rounded-lg border border-line bg-raised p-6">
              <side.Icon aria-hidden="true" size={32} weight="bold" />
              <h3 className="text-2xl font-bold">{side.title}</h3>
              <p className="text-lg">{side.text}</p>
              <ul className="flex flex-col gap-3 text-base text-muted">
                {side.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </article>
          </div>
        ))}
      </div>
    </Section>
  );
};
