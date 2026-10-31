"use client";

import { formatDay, formatNumber } from "@/lib/format";
import { Flap } from "./flap";
import { useLive } from "./live-context";

export const HeroProof: React.FC = () => {
  const { snapshot } = useLive();
  const { scrutins, legislature, latestDate } = snapshot.counters;
  if (scrutins === null || latestDate === null) {
    return <p className="text-sm text-muted">Chiffres en direct momentanément indisponibles.</p>;
  }
  const figure = formatNumber(scrutins);
  return (
    <div className="flex flex-col gap-3">
      <Flap value={figure} label={`${figure} scrutins`} className="text-4xl font-semibold sm:text-5xl" />
      <p className="text-sm text-ink-soft">
        votes (scrutins) enregistrés depuis le début de la {legislature ?? 17}e législature, le mandat actuel des
        députés.
        <br />
        Dernier vote le{" "}
        <time dateTime={latestDate} className="font-bold text-ink">
          {formatDay(latestDate)}
        </time>
        .
        <br />
        Votes consultables depuis le{" "}
        <time dateTime="2012-07-03" className="font-bold text-ink">
          3 juillet 2012
        </time>
        .
      </p>
    </div>
  );
};
