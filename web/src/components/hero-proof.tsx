"use client";

import { formatDay, formatNumber } from "@/lib/format";
import { useLive } from "./live-context";

export const HeroProof: React.FC = () => {
  const { snapshot } = useLive();
  const { scrutins, legislature, latestDate } = snapshot.counters;
  if (scrutins === null || latestDate === null) {
    return <p className="text-sm text-muted">Chiffres en direct momentanément indisponibles.</p>;
  }
  return (
    <div className="flex flex-col gap-2">
      <p className="tabular text-6xl font-bold text-accent">{formatNumber(scrutins)}</p>
      <p className="max-w-hero text-sm text-muted">
        scrutins sous la {legislature ?? 17}e législature. Dernier vote le{" "}
        <time dateTime={latestDate} className="font-bold text-ink">
          {formatDay(latestDate)}
        </time>
        .
      </p>
    </div>
  );
};
