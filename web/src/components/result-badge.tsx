import { CheckIcon, QuestionIcon, XIcon } from "@phosphor-icons/react/dist/ssr";
import type { VoteResult } from "@/lib/civix/types";
import { RESULT_LABELS } from "@/lib/format";

const ICONS = { adopte: CheckIcon, rejete: XIcon, inconnu: QuestionIcon } as const;

export const ResultBadge: React.FC<{ result: VoteResult }> = ({ result }) => {
  const Icon = ICONS[result];
  return (
    <span className="inline-flex shrink-0 items-center gap-1 rounded-sm bg-flap px-1.5 py-0.5 font-display text-sm font-semibold uppercase tracking-wide text-flap-ink">
      <Icon aria-hidden="true" size={14} weight="bold" />
      {RESULT_LABELS[result]}
    </span>
  );
};
