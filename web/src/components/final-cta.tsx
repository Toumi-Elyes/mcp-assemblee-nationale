import { CtaLink } from "./cta-link";
import { Reveal } from "./reveal";

export const FinalCta: React.FC = () => {
  return (
    <section aria-labelledby="cta-final-titre" className="py-16 sm:py-24">
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <Reveal className="flex flex-col items-start gap-6 rounded-3xl border border-line bg-surface p-6 sm:p-10">
          <h2 id="cta-final-titre" className="max-w-hero text-4xl font-semibold tracking-tight">
            Posez votre prochaine question avec les vrais chiffres
          </h2>
          <p className="max-w-hero text-lg text-muted">
            Une adresse à coller dans votre assistant, et chaque vote devient vérifiable.
          </p>
          <div className="flex flex-col items-start gap-3">
            <CtaLink />
            <p className="text-sm text-muted">Gratuit, sans compte, sans clé. Pour Claude et ChatGPT.</p>
          </div>
        </Reveal>
      </div>
    </section>
  );
};
