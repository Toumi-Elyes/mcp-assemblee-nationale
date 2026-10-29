export function fold(text: string): string {
  return text
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[-'’]/g, " ");
}

export function tokens(text: string): string[] {
  return fold(text).split(/\s+/).filter((token) => token !== "");
}

export function matchesName(fullName: string, query: string): boolean {
  const wanted = tokens(query);
  if (wanted.length === 0) {
    return false;
  }
  const haystack = tokens(fullName).join(" ");
  return wanted.every((token) => haystack.includes(token));
}

export function capitalize(text: string): string {
  return text.charAt(0).toLocaleUpperCase("fr-FR") + text.slice(1);
}

export function cleanTitle(title: string): string {
  const compact = title.replace(/\s+/g, " ").trim().replace(/\.+$/, "");
  return capitalize(compact);
}

export function truncate(text: string, limit: number): string {
  if (text.length <= limit) {
    return text;
  }
  const cut = text.slice(0, limit - 1);
  const lastSpace = cut.lastIndexOf(" ");
  const kept = lastSpace > limit / 2 ? cut.slice(0, lastSpace) : cut;
  return `${kept.trimEnd()}…`;
}

const FINAL_VOTE_PATTERN = /^l[’']ensemble/i;

export function isFinalVoteTitle(title: string): boolean {
  return FINAL_VOTE_PATTERN.test(title.trim());
}

export function normalizeSearch(text: string): string {
  return fold(text).trim();
}
