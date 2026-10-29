import { LinkIcon, LockOpenIcon, ScalesIcon, DatabaseIcon } from "@phosphor-icons/react/dist/ssr";
import { formatNumber } from "@/lib/format";
import type { HeroCounters } from "@/lib/data/view-types";
import { Section } from "./section";

type Benefit = { title: string; text: string; Icon: typeof LinkIcon };

function buildBenefits(counters: HeroCounters): Benefit[] {
  const base =
    "Les décomptes officiels et le détail par groupe viennent des données ouvertes, lus au moment de la question.";
  const live =
    counters.scrutins !== null
      ? `${base} Aujourd'hui, ${formatNumber(counters.scrutins)} scrutins de la ${counters.legislature ?? 17}e législature sont consultables.`
      : base;
  return [
    {
      title: "Des réponses avec leur source",
      text: "Chaque scrutin cité renvoie vers la page de l'Assemblée nationale et celle de CIVIX. Vous vérifiez en un clic.",
      Icon: LinkIcon,
    },
    { title: "Les vrais chiffres, pas un souvenir", text: live, Icon: DatabaseIcon },
    {
      title: "Gratuit et sans compte",
      text: "Une adresse à coller. Pas de clé, pas d'inscription, aucune donnée personnelle demandée.",
      Icon: LockOpenIcon,
    },
    {
      title: "Des faits, sans classement",
      text: "Aucun député ni aucun groupe n'est noté. Les positions sont transmises telles qu'elles sont enregistrées.",
      Icon: ScalesIcon,
    },
  ];
}

export const Benefits: React.FC<{ counters: HeroCounters }> = ({ counters }) => {
  return (
    <Section split
 id="avantages" eyebrow="Ce que vous obtenez" title="Quatre garanties pour une réponse que vous pouvez vérifier">
      <ul className="grid gap-6 sm:grid-cols-2">
        {buildBenefits(counters).map((benefit) => (
          <li key={benefit.title}>
            <div className="h-full">
              <article className="flex h-full flex-col gap-3 rounded-lg border border-line bg-raised p-6 transition hover:bg-hover">
                <benefit.Icon aria-hidden="true" size={32} weight="bold" />
                <h3 className="text-xl font-bold">{benefit.title}</h3>
                <p className="text-base text-muted">{benefit.text}</p>
              </article>
            </div>
          </li>
        ))}
      </ul>
    </Section>
  );
};
