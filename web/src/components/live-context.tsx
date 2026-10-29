"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { liveSnapshotSchema } from "@/lib/data/live-schema";
import type { LiveSnapshot } from "@/lib/data/view-types";
import { POLL_INTERVAL_MS, POLL_MAX_BACKOFF_MS, createPoller } from "@/lib/polling";

const LIVE_ENDPOINT = "/api/live";
const REDUCED_DATA_QUERY = "(prefers-reduced-data: reduce)";

type LiveState = { snapshot: LiveSnapshot; updatedAt: number; changeCount: number };

const LiveContext = createContext<LiveState | null>(null);

function hasSaveData(): boolean {
  const connection: unknown = "connection" in navigator ? navigator.connection : undefined;
  return typeof connection === "object" && connection !== null && "saveData" in connection && connection.saveData === true;
}

async function fetchSnapshot(signal: AbortSignal): Promise<LiveSnapshot> {
  const response = await fetch(LIVE_ENDPOINT, { signal, headers: { accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Réponse ${response.status}`);
  }
  return liveSnapshotSchema.parse(await response.json());
}

export const LiveProvider: React.FC<{ initial: LiveSnapshot; children: React.ReactNode }> = ({ initial, children }) => {
  const [state, setState] = useState<LiveState>({
    snapshot: initial,
    updatedAt: Date.parse(initial.generatedAt),
    changeCount: 0,
  });

  useEffect(() => {
    const reducedData = window.matchMedia(REDUCED_DATA_QUERY);
    const poller = createPoller<LiveSnapshot>({
      fetchData: fetchSnapshot,
      onData: (snapshot) => {
        setState((previous) => {
          const changed =
            JSON.stringify(previous.snapshot.week) !== JSON.stringify(snapshot.week) ||
            JSON.stringify(previous.snapshot.counters) !== JSON.stringify(snapshot.counters);
          return {
            snapshot: changed ? snapshot : previous.snapshot,
            updatedAt: Date.now(),
            changeCount: changed ? previous.changeCount + 1 : previous.changeCount,
          };
        });
      },
      intervalMs: POLL_INTERVAL_MS,
      maxBackoffMs: POLL_MAX_BACKOFF_MS,
      initialAt: Date.parse(initial.generatedAt),
      now: Date.now,
      isVisible: () => document.visibilityState === "visible",
      isOnline: () => navigator.onLine,
      isDataSaver: () => reducedData.matches || hasSaveData(),
    });
    const onChange = () => {
      poller.onEnvironmentChange();
    };
    document.addEventListener("visibilitychange", onChange);
    window.addEventListener("online", onChange);
    window.addEventListener("offline", onChange);
    reducedData.addEventListener("change", onChange);
    poller.start();
    return () => {
      document.removeEventListener("visibilitychange", onChange);
      window.removeEventListener("online", onChange);
      window.removeEventListener("offline", onChange);
      reducedData.removeEventListener("change", onChange);
      poller.stop();
    };
  }, [initial.generatedAt]);

  return <LiveContext.Provider value={state}>{children}</LiveContext.Provider>;
};

export function useLive(): LiveState {
  const value = useContext(LiveContext);
  if (value === null) {
    throw new Error("useLive doit être utilisé dans un LiveProvider.");
  }
  return value;
}
