export const THEME_KEY = "theme";

export const THEME_CHOICES = ["light", "dark", "system"] as const;

export type ThemeChoice = (typeof THEME_CHOICES)[number];

export type ResolvedTheme = "light" | "dark";

type ReadableStorage = Pick<Storage, "getItem">;
type WritableStorage = Pick<Storage, "setItem">;
type ThemeRoot = { setAttribute: (name: string, value: string) => void; removeAttribute: (name: string) => void };

const THEME_VALUES = new Set<string>(THEME_CHOICES);

export function isThemeChoice(value: unknown): value is ThemeChoice {
  return typeof value === "string" && THEME_VALUES.has(value);
}

export function parseTheme(value: unknown): ThemeChoice {
  return isThemeChoice(value) ? value : "system";
}

export function readStoredTheme(storage: ReadableStorage | null | undefined): ThemeChoice {
  if (storage === null || storage === undefined) {
    return "system";
  }
  try {
    return parseTheme(storage.getItem(THEME_KEY));
  } catch {
    return "system";
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
  if (choice === "system") {
    root.removeAttribute("data-theme");
    return;
  }
  root.setAttribute("data-theme", choice);
}

export function resolveTheme(choice: ThemeChoice, prefersDark: boolean): ResolvedTheme {
  if (choice === "system") {
    return prefersDark ? "dark" : "light";
  }
  return choice;
}

export const THEME_INIT_SCRIPT = `try{var t=localStorage.getItem("${THEME_KEY}");if(t==="light"||t==="dark"){document.documentElement.setAttribute("data-theme",t)}}catch(e){}`;
