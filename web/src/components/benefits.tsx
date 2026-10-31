
type Benefit = { title: string; text: string };

const BENEFITS: readonly Benefit[] = [
  {
    title: "Des réponses avec leur source",
    text: "Chaque vote cité renvoie vers sa page sur le site de l'Assemblée nationale. Vous vérifiez en un clic.",
  },
  {
    title: "Les vrais chiffres, pas un souvenir",
    text: "Les nombres de voix et le détail par groupe viennent de l'Assemblée, lus au moment où vous posez la question.",
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
