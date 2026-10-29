import { Section } from "./section";

const ROWS = [
  {
    topic: "Les chiffres",
    alone: "Les chiffres peuvent être anciens ou approximatifs.",
    connected: "Les décomptes viennent des données ouvertes de l'Assemblée.",
  },
  {
    topic: "La vérification",
    alone: "Aucun lien ne permet de vérifier le vote cité.",
    connected: "Chaque réponse cite la page du scrutin à ouvrir.",
  },
  {
    topic: "Le bon scrutin",
    alone: "Un même texte compte plusieurs scrutins, et il est facile de les confondre.",
    connected: "Le détail par groupe et par député est lu au moment de la question.",
  },
] as const;

export const Problem: React.FC = () => {
  return (
    <Section
      id="pourquoi"
      title="Vérifier un vote prend une heure. Se fier à une réponse de mémoire, c'est risqué."
      intro="Savoir comment un député a voté oblige à fouiller assemblee-nationale.fr, scrutin par scrutin. Et un assistant IA, seul, peut répondre avec aplomb sans avoir les bons chiffres."
    >
      <table className="w-full border-collapse text-left">
        <caption className="sr-only">Un assistant seul comparé à un assistant avec le connecteur</caption>
        <thead>
          <tr className="align-top">
            <td className="hidden w-1/5 sm:table-cell" />
            <th scope="col" className="w-1/2 pb-4 pr-6 sm:w-2/5">
              <span className="block font-display text-2xl font-semibold tracking-tight">Un assistant seul</span>
              <span className="block text-base font-normal text-ink-soft">Il répond de mémoire.</span>
            </th>
            <th scope="col" className="w-1/2 pb-4 sm:w-2/5">
              <span className="block font-display text-2xl font-semibold tracking-tight">Avec le connecteur</span>
              <span className="block text-base font-normal text-ink-soft">Il va chercher le vote.</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr key={row.topic} className="border-t border-line align-top">
              <th scope="row" className="hidden py-4 pr-6 font-display text-lg font-semibold sm:table-cell">
                {row.topic}
              </th>
              <td className="py-4 pr-6 text-base text-ink-soft">{row.alone}</td>
              <td className="py-4 text-base font-medium text-ink">{row.connected}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Section>
  );
};
