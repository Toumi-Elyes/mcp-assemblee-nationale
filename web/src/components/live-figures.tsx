import { formatNumber } from "@/lib/format";
import type { HeroCounters, TrendsData, WeekData } from "@/lib/data/view-types";
import { Sparkline } from "./sparkline";

type Props = { counters: HeroCounters; week: WeekData | null; trends: TrendsData | null };

const Figure: React.FC<{ value: string; label: string; big?: boolean; children?: React.ReactNode }> = ({
  value,
  label,
  big = false,
  children,
}) => {
  return (
    <div className="flex flex-col gap-2">
      <p className={`tabular font-bold text-accent ${big ? "text-6xl" : "text-4xl"}`}>{value}</p>
      <p className="max-w-hero text-sm text-muted">{label}</p>
      {children}
    </div>
  );
};

export const LiveFigures: React.FC<Props> = ({ counters, week, trends }) => {
  const adopted = week?.groups.reduce((sum, group) => sum + group.adopted, 0) ?? 0;
  const rejected = week?.groups.reduce((sum, group) => sum + group.rejected, 0) ?? 0;
  return (
    <div className="grid gap-8 lg:grid-cols-12">
      {trends !== null ? (
        <div className="lg:col-span-6">
          <Figure
            big
            value={formatNumber(trends.perDay.total)}
            label={`scrutins en ${trends.perDay.days.length} jours${trends.perDay.coverage.complete ? "" : " (période partielle)"}`}
          >
            <Sparkline days={trends.perDay.days} label="Évolution du nombre de scrutins par jour" />
          </Figure>
        </div>
      ) : null}
      {week !== null ? (
        <div className="lg:col-span-3">
          <Figure value={formatNumber(week.total)} label={`scrutins cette semaine : ${adopted} adoptés, ${rejected} rejetés`} />
        </div>
      ) : null}
      {counters.deputes !== null && counters.groupes !== null ? (
        <div className="lg:col-span-3">
          <Figure value={formatNumber(counters.deputes)} label={`députés dans ${counters.groupes} groupes`} />
        </div>
      ) : null}
    </div>
  );
};
