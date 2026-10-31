import { describe, expect, it } from "vitest";
import { AUDIENCE_KEY, isMeasurementAllowed, storeRefusal } from "@/lib/audience";

function memoryStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => values.delete(key),
    setItem: (key, value) => values.set(key, value),
  };
}

describe("mesure d'audience", () => {
  it("mesure par défaut", () => {
    expect(isMeasurementAllowed(memoryStorage(), {})).toBe(true);
  });

  it("ne mesure plus après un refus, puis de nouveau après une acceptation", () => {
    const storage = memoryStorage();
    storeRefusal(storage, true);
    expect(storage.getItem(AUDIENCE_KEY)).toBe("refusee");
    expect(isMeasurementAllowed(storage, {})).toBe(false);
    storeRefusal(storage, false);
    expect(isMeasurementAllowed(storage, {})).toBe(true);
  });

  it("respecte le signal Global Privacy Control", () => {
    expect(isMeasurementAllowed(memoryStorage(), { globalPrivacyControl: true })).toBe(false);
  });

  it("reste utilisable sans stockage, même si le stockage lève une erreur", () => {
    expect(isMeasurementAllowed(null, {})).toBe(true);
    const broken = {
      getItem: () => {
        throw new Error("bloqué");
      },
    };
    expect(isMeasurementAllowed(broken, {})).toBe(true);
    expect(() => storeRefusal(null, true)).not.toThrow();
  });
});
