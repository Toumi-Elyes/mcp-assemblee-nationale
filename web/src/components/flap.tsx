import { cn } from "@/lib/cn";

const GAP_CHARS = new Set([" ", " ", " "]);

type FlapProps = { value: string; label?: string; className?: string };

export const Flap: React.FC<FlapProps> = ({ value, label, className }) => {
  const chars = Array.from(value);
  return (
    <span role="img" aria-label={label ?? value} className={cn("flap", className)}>
      {chars.map((char, index) =>
        GAP_CHARS.has(char) ? (
          <span key={`gap-${index}`} aria-hidden="true" className="flap-gap" />
        ) : (
          <span key={`${index}-${char}`} aria-hidden="true" className="flap-cell">
            <span className="flap-char" style={{ "--flap-index": index } as React.CSSProperties}>
              {char}
            </span>
          </span>
        ),
      )}
    </span>
  );
};
