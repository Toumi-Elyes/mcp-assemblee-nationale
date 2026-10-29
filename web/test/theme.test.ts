import { runInNewContext } from "node:vm";
import { describe, expect, it, vi } from "vitest";
import {
  THEME_INIT_SCRIPT,
  THEME_KEY,
  DEFAULT_THEME,
  applyTheme,
  parseTheme,
  readStoredTheme,
  resolveTheme,
  writeStoredTheme,
} from "@/lib/theme";

describe("theme helpers", () => {
  it("falls back to light for anything unknown", () => {
    expect(parseTheme("light")).toBe("light");
    expect(parseTheme("dark")).toBe("dark");
    expect(parseTheme("system")).toBe("system");
    expect(parseTheme("blue")).toBe("light");
    expect(parseTheme(null)).toBe("light");
    expect(parseTheme(undefined)).toBe("light");
  });

  it("reads the stored choice and survives a throwing storage", () => {
    expect(readStoredTheme({ getItem: () => "dark" })).toBe("dark");
    expect(readStoredTheme({ getItem: () => null })).toBe("light");
    expect(readStoredTheme({ getItem: () => "system" })).toBe("system");
    expect(
      readStoredTheme({
        getItem: () => {
          throw new Error("blocked");
        },
      }),
    ).toBe("light");
    expect(readStoredTheme(null)).toBe("light");
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

  it("sets data-theme for every choice, system included", () => {
    const setAttribute = vi.fn();
    applyTheme({ setAttribute }, "dark");
    expect(setAttribute).toHaveBeenCalledWith("data-theme", "dark");
    applyTheme({ setAttribute }, "light");
    expect(setAttribute).toHaveBeenCalledWith("data-theme", "light");
    applyTheme({ setAttribute }, "system");
    expect(setAttribute).toHaveBeenCalledWith("data-theme", "system");
  });

  it("defaults to the light theme", () => {
    expect(DEFAULT_THEME).toBe("light");
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

  it("applies a stored choice before paint", () => {
    expect(run("light")).toHaveBeenCalledWith("data-theme", "light");
    expect(run("dark")).toHaveBeenCalledWith("data-theme", "dark");
    expect(run("system")).toHaveBeenCalledWith("data-theme", "system");
  });

  it("leaves the attribute alone (light by default) for junk, empty or blocked storage", () => {
    expect(run("junk")).not.toHaveBeenCalled();
    expect(run(null)).not.toHaveBeenCalled();
    expect(run(null, true)).not.toHaveBeenCalled();
  });
});
