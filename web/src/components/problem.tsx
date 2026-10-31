import { Section } from "./section";

const ROWS = [
  {
    topic: "Les chiffres",
    alone: "Les chiffres peuvent être anciens ou approximatifs.",
    connected: "Les chiffres viennent directement de l'Assemblée nationale.",
  },
  {
    topic: "La vérification",
    alone: "Aucun lien ne permet de vérifier le vote cité.",
    connected: "Chaque réponse donne le lien de la page officielle du vote.",
  },
  {
    topic: "Le bon vote",
    alone: "Un même texte est voté plusieurs fois, et il est facile de confondre ces votes.",
    connected: "Il retrouve le bon vote, avec le détail par groupe et par député.",
  },
] as const;

export const Problem: React.FC = () => {
  return (
    <Section
      id="pourquoi"
      title="Vérifier un vote prend du temps. Une réponse de mémoire peut être fausse."
      intro="Il faut chercher sur assemblee-nationale.fr, vote par vote. Et un assistant IA seul peut répondre avec assurance sans avoir les bons chiffres."
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
