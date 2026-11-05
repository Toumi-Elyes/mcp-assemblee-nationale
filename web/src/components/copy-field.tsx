import { MCP_URL } from "@/lib/config";
import { cn } from "@/lib/cn";
import { CopyButton } from "./copy-button";

type CopyFieldProps = { id: string; className?: string };

// A paragraph rather than an <input>: an input never wraps, so the address was cut off on a 390 px phone.
export const CopyField: React.FC<CopyFieldProps> = ({ id, className }) => {
  return (
    <div className={cn("flex flex-col gap-2 sm:flex-row sm:items-stretch sm:gap-0", className)}>
      <p
        id={id}
        className="min-w-0 flex-1 rounded-sm border border-rule bg-bg px-3 py-2.5 font-mono text-sm text-ink wrap-anywhere sm:rounded-r-none sm:border-r-0"
      >
        <span className="sr-only">Adresse du connecteur : </span>
        <span className="select-all">{MCP_URL}</span>
      </p>
      <CopyButton value={MCP_URL} label="Copier l'adresse" attached />
    </div>
  );
};
