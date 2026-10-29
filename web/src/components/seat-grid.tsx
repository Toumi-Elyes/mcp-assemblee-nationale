import { formatNumber, formatPercent } from "@/lib/format";

export type SeatGroup = { abbr: string; label: string; size: number };

const PER_LINE = 50;
const CELL = 6;
const GAP = 2;
const STEP = CELL + GAP;

const Seats: React.FC<{ count: number }> = ({ count }) => {
  const lines = Math.max(1, Math.ceil(count / PER_LINE));
  const width = PER_LINE * STEP - GAP;
  const height = lines * STEP - GAP;
  return (
    <svg aria-hidden="true" viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="xMinYMin meet">
      {Array.from({ length: count }, (_, index) => (
        <rect
          key={index}
          x={(index % PER_LINE) * STEP}
          y={Math.floor(index / PER_LINE) * STEP}
          width={CELL}
          height={CELL}
          className="fill-ink"
        />
      ))}
    </svg>
  );
};

export const SeatGrid: React.FC<{ groups: readonly SeatGroup[] }> = ({ groups }) => {
  const total = groups.reduce((sum, group) => sum + group.size, 0);
  return (
    <figure className="flex flex-col gap-4">
      <ul className="flex flex-col border-t border-line">
        {groups.map((group) => (
          <li
            key={group.abbr}
            className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-6 gap-y-2 border-b border-line py-3 lg:grid-cols-[minmax(0,4fr)_minmax(0,6fr)_6rem]"
          >
            <p className="text-sm">
              <span className="font-display text-base font-semibold">{group.abbr}</span>{" "}
              <span className="text-ink-soft">{group.label}</span>
            </p>
            <p className="tabular text-right font-display text-base font-semibold lg:order-3">
              {formatNumber(group.size)}
              <span className="font-sans text-sm font-normal text-muted"> · {formatPercent(total === 0 ? 0 : group.size / total)}</span>
            </p>
            <div className="col-span-2 pt-1 lg:order-2 lg:col-span-1">
              <Seats count={group.size} />
            </div>
          </li>
        ))}
      </ul>
      <figcaption className="text-sm text-muted">
        Un carré par siège, {PER_LINE} par ligne. Les groupes sont classés par effectif : cet ordre ne reflète pas la
        place des groupes dans l'hémicycle.
      </figcaption>
    </figure>
  );
};
