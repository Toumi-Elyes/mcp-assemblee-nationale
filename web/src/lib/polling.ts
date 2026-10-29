export const POLL_INTERVAL_MS = 180_000;
export const POLL_MAX_BACKOFF_MS = 900_000;

export type PollerOptions<Data> = {
  fetchData: (signal: AbortSignal) => Promise<Data>;
  onData: (data: Data) => void;
  intervalMs: number;
  maxBackoffMs: number;
  initialAt: number;
  now: () => number;
  isVisible: () => boolean;
  isOnline: () => boolean;
  isDataSaver: () => boolean;
};

export type Poller = {
  start: () => void;
  stop: () => void;
  onEnvironmentChange: () => void;
};

export function createPoller<Data>(options: PollerOptions<Data>): Poller {
  let timer: ReturnType<typeof setTimeout> | undefined;
  let controller: AbortController | null = null;
  let failures = 0;
  let lastSuccessAt = options.initialAt;
  let running = false;

  const canPoll = () => options.isVisible() && options.isOnline() && !options.isDataSaver();

  const clearTimer = () => {
    clearTimeout(timer);
    timer = undefined;
  };

  const abortRequest = () => {
    controller?.abort();
    controller = null;
  };

  const schedule = (delay: number) => {
    clearTimer();
    if (!running || !canPoll()) {
      return;
    }
    timer = setTimeout(tick, Math.max(0, delay));
  };

  const tick = async () => {
    timer = undefined;
    if (!running || !canPoll()) {
      return;
    }
    abortRequest();
    const current = new AbortController();
    controller = current;
    try {
      const data = await options.fetchData(current.signal);
      if (current.signal.aborted) {
        return;
      }
      failures = 0;
      lastSuccessAt = options.now();
      options.onData(data);
      schedule(options.intervalMs);
    } catch {
      if (current.signal.aborted) {
        return;
      }
      failures += 1;
      schedule(Math.min(options.intervalMs * 2 ** failures, options.maxBackoffMs));
    } finally {
      if (controller === current) {
        controller = null;
      }
    }
  };

  const resume = () => {
    if (timer !== undefined || controller !== null) {
      return;
    }
    schedule(options.intervalMs - (options.now() - lastSuccessAt));
  };

  return {
    start: () => {
      running = true;
      resume();
    },
    stop: () => {
      running = false;
      clearTimer();
      abortRequest();
    },
    onEnvironmentChange: () => {
      if (!running) {
        return;
      }
      if (!canPoll()) {
        clearTimer();
        abortRequest();
        return;
      }
      resume();
    },
  };
}
