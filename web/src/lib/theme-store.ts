import { DEFAULT_THEME, applyTheme, readStoredTheme, writeStoredTheme, type ThemeChoice } from "./theme";

const THEME_EVENT = "theme-change";
const DARK_QUERY = "(prefers-color-scheme: dark)";

function safeStorage(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function subscribeTheme(onChange: () => void): () => void {
  window.addEventListener("storage", onChange);
  window.addEventListener(THEME_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(THEME_EVENT, onChange);
  };
}

export function getThemeSnapshot(): ThemeChoice {
  return readStoredTheme(safeStorage());
}

export function getServerThemeSnapshot(): ThemeChoice {
  return DEFAULT_THEME;
}

export function setTheme(choice: ThemeChoice): void {
  writeStoredTheme(safeStorage(), choice);
  applyTheme(document.documentElement, choice);
  window.dispatchEvent(new Event(THEME_EVENT));
}

export function subscribePrefersDark(onChange: () => void): () => void {
  const query = window.matchMedia(DARK_QUERY);
  query.addEventListener("change", onChange);
  return () => {
    query.removeEventListener("change", onChange);
  };
}

export function getPrefersDarkSnapshot(): boolean {
  return window.matchMedia(DARK_QUERY).matches;
}

export function getServerPrefersDarkSnapshot(): boolean {
  return false;
}
