export type Loaded<Value> = { ok: true; data: Value } | { ok: false };

export async function settle<Value>(promise: Promise<Value>): Promise<Loaded<Value>> {
  try {
    return { ok: true, data: await promise };
  } catch {
    return { ok: false };
  }
}
