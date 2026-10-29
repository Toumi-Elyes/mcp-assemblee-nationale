import type { DayCount } from "@/lib/stats";

const WIDTH = 100;
const HEIGHT = 24;

export const Sparkline: React.FC<{ days: readonly DayCount[]; label: string }> = ({ days, label }) => {
  const peak = Math.max(1, ...days.map((day) => day.count));
  const step = days.length > 1 ? WIDTH / (days.length - 1) : 0;
  const points = days
    .map((day, index) => `${(index * step).toFixed(2)},${(HEIGHT - (day.count / peak) * HEIGHT).toFixed(2)}`)
    .join(" ");
  return (
    <svg role="img" aria-label={label} viewBox={`0 0 ${WIDTH} ${HEIGHT}`} preserveAspectRatio="none" className="h-12 w-full overflow-visible">
      <polyline points={points} fill="none" strokeWidth={1.5} vectorEffect="non-scaling-stroke" className="stroke-accent" />
    </svg>
  );
};
