
type Benefit = { title: string; text: string };

const BENEFITS: readonly Benefit[] = [
  {
    title: "Des réponses avec leur source",
    text: "Chaque scrutin cité renvoie vers la page de l'Assemblée nationale et celle de CIVIX. Vous vérifiez en un clic.",
  },
  {
    title: "Les vrais chiffres, pas un souvenir",
    text: "Les décomptes officiels et le détail par groupe viennent des données ouvertes, lus au moment de la question.",
  },
  {
    title: "Des faits, sans classement",
    text: "Aucun député ni aucun groupe n'est noté. Les positions sont transmises telles qu'elles sont enregistrées.",
  },
];

export const Benefits: React.FC = () => {
  return (
    <section id="avantages" aria-labelledby="avantages-titre" className="pb-20 sm:pb-28">
      <div className="mx-auto grid w-full max-w-page gap-8 px-4 sm:px-6 lg:grid-cols-12 lg:gap-12">
        <h2 id="avantages-titre" className="font-display text-3xl font-semibold tracking-tight lg:col-span-4">
          Des réponses que vous pouvez vérifier
        </h2>
        <dl className="grid gap-x-10 sm:grid-cols-3 lg:col-span-8">
          {BENEFITS.map((benefit) => (
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
