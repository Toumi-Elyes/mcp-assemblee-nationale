import { MCP_URL } from "@/lib/config";
import { cn } from "@/lib/cn";
import { CopyButton } from "./copy-button";

type CopyFieldProps = { id: string; className?: string };

export const CopyField: React.FC<CopyFieldProps> = ({ id, className }) => {
  return (
    <div className={cn("flex flex-col gap-2 sm:flex-row sm:items-stretch sm:gap-0", className)}>
      <label htmlFor={id} className="sr-only">
        Adresse du connecteur
      </label>
      <input
        id={id}
        readOnly
        value={MCP_URL}
        spellCheck={false}
        className="min-w-0 flex-1 rounded-sm border border-rule bg-bg px-3 py-2.5 font-mono text-sm text-ink sm:rounded-r-none sm:border-r-0"
      />
      <CopyButton value={MCP_URL} label="Copier l'adresse" attached />
    </div>
  );
};
