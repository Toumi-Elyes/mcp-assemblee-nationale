import { runInNewContext } from "node:vm";
import { describe, expect, it, vi } from "vitest";
import {
  THEME_INIT_SCRIPT,
  THEME_KEY,
  applyTheme,
  parseTheme,
  readStoredTheme,
  resolveTheme,
  writeStoredTheme,
} from "@/lib/theme";

describe("theme helpers", () => {
  it("falls back to system for anything unknown", () => {
    expect(parseTheme("light")).toBe("light");
    expect(parseTheme("dark")).toBe("dark");
    expect(parseTheme("system")).toBe("system");
    expect(parseTheme("blue")).toBe("system");
    expect(parseTheme(null)).toBe("system");
    expect(parseTheme(undefined)).toBe("system");
  });

  it("reads the stored choice and survives a throwing storage", () => {
    expect(readStoredTheme({ getItem: () => "dark" })).toBe("dark");
    expect(readStoredTheme({ getItem: () => null })).toBe("system");
    expect(
      readStoredTheme({
        getItem: () => {
          throw new Error("blocked");
        },
      }),
    ).toBe("system");
    expect(readStoredTheme(null)).toBe("system");
  });

  it("writes under the theme key and reports failures", () => {
    const setItem = vi.fn();
    expect(writeStoredTheme({ setItem }, "light")).toBe(true);
    expect(setItem).toHaveBeenCalledWith(THEME_KEY, "light");
    expect(
      writeStoredTheme(
        {
          setItem: () => {
            throw new Error("quota");
          },
        },
        "dark",
      ),
    ).toBe(false);
    expect(writeStoredTheme(null, "dark")).toBe(false);
  });

  it("sets data-theme for light and dark and removes it for system", () => {
    const setAttribute = vi.fn();
    const removeAttribute = vi.fn();
    applyTheme({ setAttribute, removeAttribute }, "dark");
    expect(setAttribute).toHaveBeenCalledWith("data-theme", "dark");
    applyTheme({ setAttribute, removeAttribute }, "system");
    expect(removeAttribute).toHaveBeenCalledWith("data-theme");
  });

  it("resolves system from the device preference", () => {
    expect(resolveTheme("system", true)).toBe("dark");
    expect(resolveTheme("system", false)).toBe("light");
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });
});

describe("THEME_INIT_SCRIPT", () => {
  function run(stored: string | null, throwing = false) {
    const setAttribute = vi.fn();
    runInNewContext(THEME_INIT_SCRIPT, {
      localStorage: {
        getItem: () => {
          if (throwing) {
            throw new Error("blocked");
          }
          return stored;
        },
      },
      document: { documentElement: { setAttribute } },
    });
    return setAttribute;
  }

  it("applies a stored light or dark choice before paint", () => {
    expect(run("light")).toHaveBeenCalledWith("data-theme", "light");
    expect(run("dark")).toHaveBeenCalledWith("data-theme", "dark");
  });

  it("leaves the attribute alone for system, junk or blocked storage", () => {
    expect(run("system")).not.toHaveBeenCalled();
    expect(run("junk")).not.toHaveBeenCalled();
    expect(run(null)).not.toHaveBeenCalled();
    expect(run(null, true)).not.toHaveBeenCalled();
  });
});
