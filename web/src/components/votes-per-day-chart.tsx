import type { VotesPerDay } from "@/lib/stats";
import { formatShortDay } from "@/lib/format";

const CHART_WIDTH = 300;
const CHART_HEIGHT = 80;
const BAR_GAP_RATIO = 0.25;

export const VotesPerDayChart: React.FC<{ data: VotesPerDay }> = ({ data }) => {
  const peak = Math.max(1, ...data.days.map((day) => day.count));
  const slot = CHART_WIDTH / Math.max(data.days.length, 1);
  const first = data.days[0];
  const last = data.days.at(-1);
  return (
    <figure className="flex flex-col gap-3">
      <svg
        role="img"
        aria-label={`Scrutins par jour du ${first ? formatShortDay(first.date) : ""} au ${last ? formatShortDay(last.date) : ""}, ${data.total} au total, maximum ${peak} en une journée`}
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        preserveAspectRatio="none"
        className="h-24 w-full"
      >
        {data.days.map((day, index) => {
          const height = (day.count / peak) * CHART_HEIGHT;
          return (
            <rect
              key={day.date}
              x={index * slot + (slot * BAR_GAP_RATIO) / 2}
              y={CHART_HEIGHT - height}
              width={slot * (1 - BAR_GAP_RATIO)}
              height={height}
              className="fill-accent"
            >
              <title>{`${formatShortDay(day.date)} : ${day.count} scrutins`}</title>
            </rect>
          );
        })}
      </svg>
      <figcaption className="flex justify-between text-xs text-muted">
        <span>{first ? formatShortDay(first.date) : ""}</span>
        <span className="tabular font-mono">max {peak} par jour</span>
        <span>{last ? formatShortDay(last.date) : ""}</span>
      </figcaption>
    </figure>
  );
};
