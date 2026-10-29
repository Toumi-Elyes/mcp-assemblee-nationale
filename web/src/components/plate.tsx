import { cn } from "@/lib/cn";

type PlateProps = {
  number: number;
  title: string;
  note?: string;
  className?: string;
  children: React.ReactNode;
};

export const Plate: React.FC<PlateProps> = ({ number, title, note, className, children }) => {
  return (
    <section aria-label={title} className={cn("flex flex-col gap-4 border-t-2 border-rule pt-3", className)}>
      <header className="flex flex-col gap-1">
        <h3 className="font-display text-2xl font-semibold leading-tight tracking-tight">{title}</h3>
        <p className="text-sm text-ink-soft">
          <span className="font-semibold text-ink">Tableau {number}.</span>
          {note !== undefined ? ` ${note}` : null}
        </p>
      </header>
      {children}
    </section>
  );
};
