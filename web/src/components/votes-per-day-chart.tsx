import { formatLongDay, formatNumber, formatShortDay } from "@/lib/format";
import type { VotesPerDay } from "@/lib/stats";

const WIDTH = 720;
const HEIGHT = 240;
const PAD = { top: 12, right: 8, bottom: 28, left: 36 };
const GRID_LINES = 4;
const LABEL_EVERY = 5;

const niceMax = (value: number): number => {
  if (value <= 4) {
    return 4;
  }
  const magnitude = 10 ** Math.floor(Math.log10(value));
  return Math.ceil(value / magnitude) * magnitude;
};

export const VotesPerDayChart: React.FC<{ data: VotesPerDay }> = ({ data }) => {
  const { days, coverage, total } = data;
  const peak = niceMax(Math.max(...days.map((day) => day.count), 0));
  const innerWidth = WIDTH - PAD.left - PAD.right;
  const innerHeight = HEIGHT - PAD.top - PAD.bottom;
  const step = innerWidth / Math.max(days.length, 1);
  const barWidth = Math.max(step * 0.7, 2);
  const summary = `Nombre de scrutins par jour du ${formatShortDay(coverage.from)} au ${formatShortDay(coverage.to)} : ${formatNumber(total)} au total.`;

  return (
    <figure>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={summary} className="h-auto w-full">
        {Array.from({ length: GRID_LINES + 1 }, (_, index) => {
          const value = (peak / GRID_LINES) * index;
          const y = PAD.top + innerHeight - (value / peak) * innerHeight;
          return (
            <g key={index}>
              <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y} y2={y} style={{ stroke: "var(--border)" }} />
              <text x={PAD.left - 6} y={y + 4} textAnchor="end" fontSize="11" style={{ fill: "var(--muted)" }}>
                {Math.round(value)}
              </text>
            </g>
          );
        })}
        {days.map((day, index) => {
          const height = (day.count / peak) * innerHeight;
          const x = PAD.left + index * step + (step - barWidth) / 2;
          const showLabel = index % LABEL_EVERY === 0 || index === days.length - 1;
          return (
            <g key={day.date}>
              <rect
                x={x}
                y={PAD.top + innerHeight - height}
                width={barWidth}
                height={height}
                rx={1.5}
                style={{ fill: "var(--bar)" }}
              >
                <title>{`${formatLongDay(day.date)} : ${day.count} scrutin${day.count > 1 ? "s" : ""}`}</title>
              </rect>
              {showLabel ? (
                <text
                  x={x + barWidth / 2}
                  y={HEIGHT - 8}
                  textAnchor="middle"
                  fontSize="11"
                  style={{ fill: "var(--muted)" }}
                >
                  {formatShortDay(day.date)}
                </text>
              ) : null}
            </g>
          );
        })}
      </svg>
      <figcaption className="mt-2 text-sm text-muted">
        {summary}
        {coverage.complete ? "" : " Période limitée aux votes récupérés."}
      </figcaption>
      <details className="mt-2 text-sm">
        <summary className="cursor-pointer text-accent">Voir les valeurs jour par jour</summary>
        <table className="mt-2 w-full max-w-sm text-left">
          <caption className="sr-only">Scrutins par jour</caption>
          <thead>
            <tr>
              <th scope="col" className="py-1 pr-4 font-semibold">
                Jour
              </th>
              <th scope="col" className="py-1 font-semibold">
                Scrutins
              </th>
            </tr>
          </thead>
          <tbody>
            {days.map((day) => (
              <tr key={day.date} className="border-t border-line">
                <td className="py-1 pr-4">{formatLongDay(day.date)}</td>
                <td className="py-1 tabular-nums">{day.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
};
