import { cn } from "@/lib/cn";
import { Reveal } from "./reveal";

type SectionProps = {
  id?: string;
  eyebrow?: string;
  title: string;
  intro?: string;
  tone?: "plain" | "surface";
  children: React.ReactNode;
  className?: string;
};

export const Section: React.FC<SectionProps> = ({
  id,
  eyebrow,
  title,
  intro,
  tone = "plain",
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
      <div className="mx-auto w-full max-w-page px-4 sm:px-6">
        <Reveal className="flex max-w-hero flex-col gap-3">
          {eyebrow !== undefined ? (
            <p className="text-sm font-semibold text-muted">{eyebrow}</p>
          ) : null}
          <h2 id={headingId} className="text-4xl font-semibold tracking-tight">
            {title}
          </h2>
          {intro !== undefined ? <p className="text-lg text-muted">{intro}</p> : null}
        </Reveal>
        <div className="mt-10 sm:mt-12">{children}</div>
      </div>
    </section>
  );
};
