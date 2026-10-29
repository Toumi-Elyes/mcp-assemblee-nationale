import type { Counts } from "@/lib/civix/types";
import { formatNumber } from "@/lib/format";

const SEGMENTS = [
  { key: "pour", label: "Pour", fill: "fill-pour" },
  { key: "contre", label: "Contre", fill: "fill-contre" },
  { key: "abstention", label: "Abstention", fill: "fill-abstention" },
  { key: "non_votant", label: "Non votant", fill: "fill-absent" },
] as const;

export const PositionBar: React.FC<{ counts: Counts; label: string }> = ({ counts, label }) => {
  const total = counts.pour + counts.contre + counts.abstention + counts.non_votant;
  const summary = `${label} : ${SEGMENTS.map((segment) => `${formatNumber(counts[segment.key])} ${segment.label.toLowerCase()}`).join(", ")}`;
  const placed = SEGMENTS.reduce<Array<{ key: string; fill: string; x: number; width: number }>>((list, segment) => {
    const width = total === 0 ? 0 : (counts[segment.key] / total) * 100;
    const x = list.reduce((sum, item) => sum + item.width, 0);
    return [...list, { key: segment.key, fill: segment.fill, x, width }];
  }, []);
  return (
    <svg role="img" aria-label={summary} className="h-2 w-full overflow-hidden rounded-sm" preserveAspectRatio="none">
      {total === 0 ? <rect width="100%" height="100%" className="fill-absent" /> : null}
      {placed.map((segment) => (
        <rect key={segment.key} x={`${segment.x}%`} width={`${segment.width}%`} height="100%" className={segment.fill} />
      ))}
    </svg>
  );
};

export const PositionLegend: React.FC<{ counts: Counts }> = ({ counts }) => {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
      {SEGMENTS.map((segment) => (
        <li key={segment.key} className="flex items-center gap-1">
          <svg aria-hidden="true" viewBox="0 0 12 12" className="size-3">
            <circle cx="6" cy="6" r="6" className={segment.fill} />
          </svg>
          <span className="text-muted">{segment.label}</span>
          <span className="tabular font-mono font-medium">{formatNumber(counts[segment.key])}</span>
        </li>
      ))}
    </ul>
  );
};
