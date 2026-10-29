import { cn } from "@/lib/cn";

type SectionProps = {
  id?: string;
  eyebrow?: string;
  title: string;
  intro?: string;
  tone?: "plain" | "surface";
  split?: boolean;
  children: React.ReactNode;
  className?: string;
};

export const Section: React.FC<SectionProps> = ({
  id,
  eyebrow,
  title,
  intro,
  tone = "plain",
  split = false,
  children,
  className,
}) => {
  const headingId = id !== undefined ? `${id}-titre` : undefined;
  return (
    <section
      id={id}
      aria-labelledby={headingId}
      className={cn("py-16 sm:py-24", tone === "surface" ? "bg-surface" : undefined, className)}
    >
      <div className={cn("mx-auto w-full max-w-page px-4 sm:px-6", split ? "grid gap-10 lg:grid-cols-12 lg:gap-12" : undefined)}>
        <div
          className={cn(
            "flex flex-col gap-3",
            split ? "lg:sticky lg:top-6 lg:col-span-4 lg:self-start" : "max-w-hero",
          )}
        >
          {eyebrow !== undefined ? (
            <p className="text-sm font-bold text-muted">{eyebrow}</p>
          ) : null}
          <h2 id={headingId} className="font-serif text-4xl font-bold">
            {title}
          </h2>
          {intro !== undefined ? <p className="text-lg text-muted">{intro}</p> : null}
        </div>
        <div className={split ? "lg:col-span-8" : "mt-10 sm:mt-12"}>{children}</div>
      </div>
    </section>
  );
};
