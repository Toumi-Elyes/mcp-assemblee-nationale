import { formatNumber, pluralize } from "@/lib/format";
import type { HeroCounters, TrendsData, WeekData } from "@/lib/data/view-types";
import { Flap } from "./flap";

type Props = { counters: HeroCounters; week: WeekData | null; trends: TrendsData | null };

const Figure: React.FC<{ value: number; label: string }> = ({ value, label }) => {
  const text = formatNumber(value);
  return (
    <li className="flex items-center gap-4 border-b border-line py-4 sm:border-b-0 sm:border-r sm:px-6 sm:first:pl-0 sm:last:border-r-0">
      <Flap value={text} label={text} className="text-4xl font-semibold" />
      <span className="max-w-48 text-sm text-ink-soft">{label}</span>
    </li>
  );
};

export const LiveFigures: React.FC<Props> = ({ counters, week, trends }) => {
  const adopted = week?.groups.reduce((sum, group) => sum + group.adopted, 0) ?? 0;
  const rejected = week?.groups.reduce((sum, group) => sum + group.rejected, 0) ?? 0;
  return (
    <ul className="flex flex-col sm:flex-row sm:flex-wrap">
      {trends !== null ? (
        <Figure
          value={trends.perDay.total}
          label={`scrutins en ${trends.perDay.days.length} jours${trends.perDay.coverage.complete ? "" : " (période partielle)"}`}
        />
      ) : null}
      {week !== null ? (
        <Figure value={week.total} label={`scrutins cette semaine : ${pluralize(adopted, "adopté")}, ${pluralize(rejected, "rejeté")}`} />
      ) : null}
      {counters.deputes !== null && counters.groupes !== null ? (
        <Figure value={counters.deputes} label={`députés dans ${counters.groupes} groupes`} />
      ) : null}
    </ul>
  );
};
