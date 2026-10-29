import { MCP_URL } from "@/lib/config";
import { CopyButton } from "./copy-button";

export const CopyField: React.FC = () => {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-line bg-raised p-2 sm:flex-row sm:items-center">
      <label htmlFor="adresse-connecteur" className="sr-only">
        Adresse du connecteur
      </label>
      <input
        id="adresse-connecteur"
        readOnly
        value={MCP_URL}
        spellCheck={false}
        className="min-w-0 flex-1 rounded bg-surface px-3 py-2 font-mono text-sm text-ink"
      />
      <CopyButton value={MCP_URL} label="Copier l'adresse" />
    </div>
  );
};
