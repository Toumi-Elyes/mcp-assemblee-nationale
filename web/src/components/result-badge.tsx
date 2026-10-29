import { CheckCircleIcon, QuestionIcon, XCircleIcon } from "@phosphor-icons/react/dist/ssr";
import type { VoteResult } from "@/lib/civix/types";
import { RESULT_LABELS } from "@/lib/format";

const ICONS = { adopte: CheckCircleIcon, rejete: XCircleIcon, inconnu: QuestionIcon } as const;

export const ResultBadge: React.FC<{ result: VoteResult }> = ({ result }) => {
  const Icon = ICONS[result];
  return (
    <span className="inline-flex items-center gap-1 rounded border border-line bg-raised px-2 py-0.5 text-sm font-bold">
      <Icon aria-hidden="true" size={16} weight="bold" />
      {RESULT_LABELS[result]}
    </span>
  );
};
