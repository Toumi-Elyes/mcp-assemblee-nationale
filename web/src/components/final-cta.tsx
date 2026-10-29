import { CtaLink } from "./cta-link";

export const FinalCta: React.FC = () => {
  return (
    <section aria-labelledby="cta-final-titre" className="bg-surface py-16 sm:py-24">
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <div className="flex flex-col items-start gap-6 rounded-lg border border-line bg-raised p-6 sm:p-10">
          <h2 id="cta-final-titre" className="max-w-hero font-serif text-4xl font-bold">
            Posez votre prochaine question avec les vrais chiffres
          </h2>
          <p className="max-w-hero text-lg text-muted">
            Une adresse à coller dans votre assistant, et chaque vote devient vérifiable.
          </p>
          <div className="flex flex-col items-start gap-3">
            <CtaLink />
            <p className="text-sm text-muted">Gratuit, sans compte, sans clé. Pour Claude et ChatGPT.</p>
          </div>
        </div>
      </div>
    </section>
  );
};
