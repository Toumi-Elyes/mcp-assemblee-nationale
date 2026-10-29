import { formatNumber } from "@/lib/format";
import type { HeroCounters } from "@/lib/data/view-types";

type Benefit = { title: string; text: string };

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
    },
    { title: "Les vrais chiffres, pas un souvenir", text: live },
    {
      title: "Gratuit et sans compte",
      text: "Une adresse à coller. Pas de clé, pas d'inscription, aucune donnée personnelle demandée.",
    },
    {
      title: "Des faits, sans classement",
      text: "Aucun député ni aucun groupe n'est noté. Les positions sont transmises telles qu'elles sont enregistrées.",
    },
  ];
}

export const Benefits: React.FC<{ counters: HeroCounters }> = ({ counters }) => {
  return (
    <section id="avantages" aria-labelledby="avantages-titre" className="pb-16 sm:pb-20">
      <div className="mx-auto grid w-full max-w-page gap-8 px-4 sm:px-6 lg:grid-cols-12 lg:gap-12">
        <h2 id="avantages-titre" className="font-display text-3xl font-semibold tracking-tight lg:col-span-4">
          Quatre garanties pour une réponse que vous pouvez vérifier
        </h2>
        <dl className="grid gap-x-12 sm:grid-cols-2 lg:col-span-8">
          {buildBenefits(counters).map((benefit) => (
            <div key={benefit.title} className="flex flex-col gap-2 border-t border-rule py-5">
              <dt className="font-display text-xl font-semibold leading-tight">{benefit.title}</dt>
              <dd className="text-base text-ink-soft">{benefit.text}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
};
