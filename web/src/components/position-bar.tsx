import type { Counts } from "@/lib/civix/types";
import { POSITION_LABELS, formatNumber } from "@/lib/format";

const SEGMENTS = [
  { key: "pour", color: "var(--pos-pour)" },
  { key: "contre", color: "var(--pos-contre)" },
  { key: "abstention", color: "var(--pos-abstention)" },
  { key: "non_votant", color: "var(--pos-non-votant)" },
] as const;

type PositionBarProps = { counts: Counts; className?: string; height?: string };

export const PositionBar: React.FC<PositionBarProps> = ({ counts, className, height = "h-3" }) => {
  const total = counts.pour + counts.contre + counts.abstention + counts.non_votant;
  const summary = SEGMENTS.map(
    (segment) => `${POSITION_LABELS[segment.key]} : ${formatNumber(counts[segment.key])}`,
  ).join(", ");
  if (total === 0) {
    return <div className={`${height} w-full rounded-full bg-surface-2 ${className ?? ""}`} aria-label="Aucun vote" role="img" />;
  }
  return (
    <div
      role="img"
      aria-label={summary}
      className={`flex ${height} w-full overflow-hidden rounded-full bg-surface-2 ${className ?? ""}`}
    >
      {SEGMENTS.map((segment) => {
        const value = counts[segment.key];
        return value > 0 ? (
          <div key={segment.key} style={{ width: `${(value / total) * 100}%`, background: segment.color }} />
        ) : null;
      })}
    </div>
  );
};

export const PositionLegend: React.FC = () => {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
      {SEGMENTS.map((segment) => (
        <li key={segment.key} className="flex items-center gap-1.5">
          <span aria-hidden className="size-2.5 rounded-sm" style={{ background: segment.color }} />
          {POSITION_LABELS[segment.key]}
        </li>
      ))}
    </ul>
  );
};

export const CountsText: React.FC<{ counts: Counts }> = ({ counts }) => {
  return (
    <span className="tabular-nums">
      {formatNumber(counts.pour)} pour · {formatNumber(counts.contre)} contre ·{" "}
      {formatNumber(counts.abstention)} abstention{counts.abstention > 1 ? "s" : ""}
    </span>
  );
};
