import { InstallLine } from "./install-line";

export const FinalCta: React.FC = () => {
  return (
    <section aria-labelledby="cta-final-titre" className="border-t-2 border-rule py-16 sm:py-24">
      <div className="mx-auto flex w-full max-w-page flex-col gap-12 px-4 sm:px-6">
        <div className="flex flex-col gap-4">
          <h2 id="cta-final-titre" className="max-w-4xl font-display text-5xl font-semibold leading-none tracking-tight sm:text-6xl">
            Posez votre prochaine question avec les vrais chiffres
          </h2>
          <p className="max-w-measure text-lg text-ink-soft">
            Une adresse à coller dans votre assistant, et chaque vote devient vérifiable.
          </p>
        </div>
        <InstallLine fieldId="adresse-connecteur-fin" headingId="ajouter-fin-titre" />
      </div>
    </section>
  );
};
