import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createPoller, POLL_INTERVAL_MS, POLL_MAX_BACKOFF_MS } from "@/lib/polling";

type Environment = { visible: boolean; online: boolean; dataSaver: boolean };

function setup(overrides: { fetchData?: (signal: AbortSignal) => Promise<string>; ageMs?: number } = {}) {
  const environment: Environment = { visible: true, online: true, dataSaver: false };
  const fetchData = vi.fn(overrides.fetchData ?? (() => Promise.resolve("data")));
  const onData = vi.fn();
  const poller = createPoller<string>({
    fetchData,
    onData,
    intervalMs: POLL_INTERVAL_MS,
    maxBackoffMs: POLL_MAX_BACKOFF_MS,
    initialAt: Date.now() - (overrides.ageMs ?? 0),
    now: Date.now,
    isVisible: () => environment.visible,
    isOnline: () => environment.online,
    isDataSaver: () => environment.dataSaver,
  });
  return { environment, fetchData, onData, poller };
}

describe("createPoller", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-29T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("polls every three minutes while the tab is visible", async () => {
    const { fetchData, onData, poller } = setup();
    poller.start();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS - 1);
    expect(fetchData).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1);
    expect(fetchData).toHaveBeenCalledTimes(1);
    expect(onData).toHaveBeenCalledWith("data");
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    expect(fetchData).toHaveBeenCalledTimes(2);
    poller.stop();
  });

  it("fetches right away when the server render is already stale", async () => {
    const { fetchData, poller } = setup({ ageMs: 30 * 60_000 });
    poller.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(fetchData).toHaveBeenCalledTimes(1);
    poller.stop();
  });

  it("pauses while hidden and refreshes once on return when stale", async () => {
    const { environment, fetchData, poller } = setup();
    poller.start();
    environment.visible = false;
    poller.onEnvironmentChange();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 5);
    expect(fetchData).not.toHaveBeenCalled();
    environment.visible = true;
    poller.onEnvironmentChange();
    await vi.advanceTimersByTimeAsync(0);
    expect(fetchData).toHaveBeenCalledTimes(1);
    poller.stop();
  });

  it("does not refresh immediately on return when data is still fresh", async () => {
    const { environment, fetchData, poller } = setup();
    poller.start();
    await vi.advanceTimersByTimeAsync(60_000);
    environment.visible = false;
    poller.onEnvironmentChange();
    environment.visible = true;
    poller.onEnvironmentChange();
    await vi.advanceTimersByTimeAsync(0);
    expect(fetchData).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS - 60_000);
    expect(fetchData).toHaveBeenCalledTimes(1);
    poller.stop();
  });

  it("stays idle when offline or when reduced data is requested", async () => {
    const { environment, fetchData, poller } = setup();
    environment.online = false;
    poller.start();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 3);
    expect(fetchData).not.toHaveBeenCalled();
    environment.online = true;
    environment.dataSaver = true;
    poller.onEnvironmentChange();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 3);
    expect(fetchData).not.toHaveBeenCalled();
    poller.stop();
  });

  it("backs off exponentially after errors, up to fifteen minutes, and resets after a success", async () => {
    let fail = true;
    const { fetchData, poller } = setup({
      fetchData: () => (fail ? Promise.reject(new Error("down")) : Promise.resolve("data")),
    });
    poller.start();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    expect(fetchData).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 2 - 1);
    expect(fetchData).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);
    expect(fetchData).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 4);
    expect(fetchData).toHaveBeenCalledTimes(3);
    await vi.advanceTimersByTimeAsync(POLL_MAX_BACKOFF_MS - 1);
    expect(fetchData).toHaveBeenCalledTimes(3);
    await vi.advanceTimersByTimeAsync(1);
    expect(fetchData).toHaveBeenCalledTimes(4);
    fail = false;
    await vi.advanceTimersByTimeAsync(POLL_MAX_BACKOFF_MS);
    expect(fetchData).toHaveBeenCalledTimes(5);
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    expect(fetchData).toHaveBeenCalledTimes(6);
    poller.stop();
  });

  it("aborts the in flight request when stopped and ignores its result", async () => {
    let captured: AbortSignal | null = null;
    const { onData, poller } = setup({
      fetchData: (signal) => {
        captured = signal;
        return new Promise<string>((resolve) => {
          signal.addEventListener("abort", () => {
            resolve("late");
          });
        });
      },
    });
    poller.start();
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS);
    expect(captured).not.toBeNull();
    poller.stop();
    expect((captured as AbortSignal | null)?.aborted).toBe(true);
    await vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * 2);
    expect(onData).not.toHaveBeenCalled();
  });
});
