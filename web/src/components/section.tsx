import { cn } from "@/lib/cn";

type SectionProps = {
  id?: string;
  title: string;
  intro?: React.ReactNode;
  meta?: React.ReactNode;
  tone?: "plain" | "surface";
  children: React.ReactNode;
  className?: string;
};

export const Section: React.FC<SectionProps> = ({ id, title, intro, meta, tone = "plain", children, className }) => {
  const headingId = id !== undefined ? `${id}-titre` : undefined;
  return (
    <section
      id={id}
      aria-labelledby={headingId}
      className={cn("py-20 sm:py-28", tone === "surface" ? "bg-surface" : undefined, className)}
    >
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <header className="flex flex-col gap-4 border-b-2 border-rule pb-5 lg:flex-row lg:items-end lg:justify-between lg:gap-12">
          <div className="flex max-w-3xl flex-col gap-3">
            <h2 id={headingId} className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
              {title}
            </h2>
            {intro !== undefined ? <p className="max-w-measure text-lg text-ink-soft">{intro}</p> : null}
          </div>
          {meta !== undefined ? <div className="shrink-0 text-sm text-muted lg:text-right">{meta}</div> : null}
        </header>
        <div className="mt-8 sm:mt-10">{children}</div>
      </div>
    </section>
  );
};
