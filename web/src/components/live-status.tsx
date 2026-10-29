"use client";

import { useEffect, useState } from "react";
import { formatTimestamp } from "@/lib/format";
import { useLive } from "./live-context";

const TICK_MS = 60_000;
const MS_PER_MINUTE = 60_000;

function relativeLabel(elapsedMs: number): string {
  const minutes = Math.floor(elapsedMs / MS_PER_MINUTE);
  if (minutes < 1) {
    return "à l'instant";
  }
  return `il y a ${minutes} min`;
}

export const LiveStatus: React.FC = () => {
  const { updatedAt, changeCount } = useLive();
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    const tick = () => {
      setNow(Date.now());
    };
    tick();
    const id = window.setInterval(tick, TICK_MS);
    return () => {
      window.clearInterval(id);
    };
  }, []);

  return (
    <p className="text-sm text-muted">
      {now === null
        ? `Dernière lecture : ${formatTimestamp(new Date(updatedAt))}.`
        : `Mis à jour ${relativeLabel(Math.max(0, now - updatedAt))}.`}
      <span aria-live="polite" className="sr-only">
        {changeCount > 0 ? "De nouvelles données ont été chargées." : ""}
      </span>
    </p>
  );
};
