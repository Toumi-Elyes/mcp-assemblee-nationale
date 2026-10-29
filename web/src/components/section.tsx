import type { ReactNode } from "react";

type SectionProps = {
  id: string;
  eyebrow?: string;
  title: string;
  intro?: ReactNode;
  children: ReactNode;
};

export const Section: React.FC<SectionProps> = ({ id, eyebrow, title, intro, children }) => {
  return (
    <section
      id={id}
      aria-labelledby={`${id}-title`}
      className="mx-auto w-full max-w-6xl px-4 py-12 sm:px-6 sm:py-16"
    >
      <header className="mb-8 max-w-3xl">
        {eyebrow !== undefined ? <p className="eyebrow mb-2">{eyebrow}</p> : null}
        <h2 id={`${id}-title`} className="section-title">
          {title}
        </h2>
        {intro !== undefined ? <p className="mt-3 text-muted">{intro}</p> : null}
      </header>
      {children}
    </section>
  );
};

export const Unavailable: React.FC = () => {
  return (
    <p role="status" className="card p-6 text-muted">
      Données momentanément indisponibles. Réessayez dans quelques minutes.
    </p>
  );
};
