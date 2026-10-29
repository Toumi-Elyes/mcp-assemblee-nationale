"use client";

import { useState } from "react";
import { hemicycleSeats } from "@/lib/stats";
import { formatNumber, formatPercent } from "@/lib/format";
import { cn } from "@/lib/cn";

export type HemicycleGroup = { abbr: string; label: string; size: number };

const SEAT_RADIUS = 1.8;

export const Hemicycle: React.FC<{ groups: readonly HemicycleGroup[] }> = ({ groups }) => {
  const [active, setActive] = useState<number | null>(null);
  const seats = hemicycleSeats(groups.map((group) => group.size));
  const total = groups.reduce((sum, group) => sum + group.size, 0);

  const fillFor = (group: number) => {
    if (active === null) {
      return group % 2 === 0 ? "fill-accent" : "fill-abstention";
    }
    return active === group ? "fill-accent" : "fill-absent";
  };

  const onHighlight = (index: number) => () => {
    setActive(index);
  };
  const onClear = () => {
    setActive(null);
  };

  return (
    <div className="grid items-center gap-8 lg:grid-cols-12">
      <figure className="lg:col-span-7">
        <svg
          role="img"
          aria-label={`Hémicycle de ${total} sièges répartis en ${groups.length} groupes. La liste à côté donne l'effectif de chacun.`}
          viewBox="0 0 200 106"
          className="w-full"
        >
          {seats.map((seat, index) => (
            <circle
              key={index}
              cx={seat.x}
              cy={seat.y}
              r={SEAT_RADIUS}
              className={cn("transition-opacity", fillFor(seat.group))}
            />
          ))}
        </svg>
        <figcaption className="mt-2 text-xs text-muted">
          Un point par siège. Survolez ou sélectionnez un groupe pour le repérer.
        </figcaption>
      </figure>
      <ul className="flex flex-col gap-1 lg:col-span-5">
        {groups.map((group, index) => (
          <li key={group.abbr}>
            <button
              type="button"
              aria-pressed={active === index}
              onMouseEnter={onHighlight(index)}
              onFocus={onHighlight(index)}
              onMouseLeave={onClear}
              onBlur={onClear}
              className={cn(
                "flex w-full items-baseline justify-between gap-3 rounded px-3 py-2 text-left text-sm transition",
                active === index ? "bg-hover" : "hover:bg-hover",
              )}
            >
              <span>
                <span className="font-bold">{group.abbr}</span> <span className="text-muted">{group.label}</span>
              </span>
              <span className="tabular shrink-0">
                {formatNumber(group.size)}
                <span className="text-muted"> · {formatPercent(total === 0 ? 0 : group.size / total)}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
