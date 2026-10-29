export const Tagline: React.FC = () => {
  return (
    <section aria-label="Notre principe" className="border-y border-line py-16 sm:py-24">
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <p className="max-w-5xl font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">
          Les chiffres viennent de l'Assemblée.{" "}
          <span className="text-ink-soft">Les liens mènent à la source.</span>{" "}
          <span className="text-muted">Le jugement vous appartient.</span>
        </p>
      </div>
    </section>
  );
};
