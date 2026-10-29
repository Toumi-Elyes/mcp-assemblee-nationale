export const THEME_KEY = "theme";

export const THEME_CHOICES = ["light", "dark", "system"] as const;

export type ThemeChoice = (typeof THEME_CHOICES)[number];

export const DEFAULT_THEME: ThemeChoice = "light";

export type ResolvedTheme = "light" | "dark";

type ReadableStorage = Pick<Storage, "getItem">;
type WritableStorage = Pick<Storage, "setItem">;
type ThemeRoot = { setAttribute: (name: string, value: string) => void };

const THEME_VALUES = new Set<string>(THEME_CHOICES);

export function isThemeChoice(value: unknown): value is ThemeChoice {
  return typeof value === "string" && THEME_VALUES.has(value);
}

export function parseTheme(value: unknown): ThemeChoice {
  return isThemeChoice(value) ? value : DEFAULT_THEME;
}

export function readStoredTheme(storage: ReadableStorage | null | undefined): ThemeChoice {
  if (storage === null || storage === undefined) {
    return DEFAULT_THEME;
  }
  try {
    return parseTheme(storage.getItem(THEME_KEY));
  } catch {
    return DEFAULT_THEME;
  }
}

export function writeStoredTheme(storage: WritableStorage | null | undefined, choice: ThemeChoice): boolean {
  if (storage === null || storage === undefined) {
    return false;
  }
  try {
    storage.setItem(THEME_KEY, choice);
    return true;
  } catch {
    return false;
  }
}

export function applyTheme(root: ThemeRoot, choice: ThemeChoice): void {
  root.setAttribute("data-theme", choice);
}

export function resolveTheme(choice: ThemeChoice, prefersDark: boolean): ResolvedTheme {
  if (choice === "system") {
    return prefersDark ? "dark" : "light";
  }
  return choice;
}

export const THEME_INIT_SCRIPT = `try{var t=localStorage.getItem("${THEME_KEY}");if(t==="light"||t==="dark"||t==="system"){document.documentElement.setAttribute("data-theme",t)}}catch(e){}`;
