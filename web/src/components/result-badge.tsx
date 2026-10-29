import { Check, X } from "lucide-react";
import type { VoteResult } from "@/lib/civix/types";
import { RESULT_LABELS } from "@/lib/format";

const STYLES: Record<VoteResult, string> = {
  adopte: "border-accent bg-accent-soft text-accent",
  rejete: "border-line bg-surface-2 text-ink",
  inconnu: "border-line text-muted",
};

export const ResultBadge: React.FC<{ result: VoteResult }> = ({ result }) => {
  return (
    <span
      className={`inline-flex items-center gap-1 whitespace-nowrap rounded-full border px-2 py-0.5 text-xs font-semibold ${STYLES[result]}`}
    >
      {result === "adopte" ? <Check aria-hidden className="size-3" /> : null}
      {result === "rejete" ? <X aria-hidden className="size-3" /> : null}
      {RESULT_LABELS[result]}
    </span>
  );
};
