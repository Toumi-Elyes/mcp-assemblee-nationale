import { CHANGE_LABELS, CHANGELOG, type ChangelogDay } from "@/content/changelog";
import { GITHUB_URL } from "@/lib/config";

/** Adresse publique de la landing, pour les liens du CHANGELOG.md lu sur GitHub. */
export const PUBLIC_SITE_URL = "https://landing-page-mcp-assemblee-national.vercel.app";

const markdownDay = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});

export function changelogDay(date: string): string {
  return markdownDay.format(new Date(`${date}T00:00:00Z`));
}

export function pullRequestUrl(pr: number): string {
  return `${GITHUB_URL}/pull/${pr}`;
}

function dayMarkdown(day: ChangelogDay): string {
  const lines = day.changes.map(
    (change) =>
      `- **${CHANGE_LABELS[change.kind]}** · ${change.title}. ${change.detail} ([#${change.pr}](${pullRequestUrl(change.pr)}))`,
  );
  return [`## ${changelogDay(day.date)}`, "", ...lines].join("\n");
}

/** CHANGELOG.md du dépôt, tiré de `content/changelog.ts` (ne pas modifier le fichier à la main). */
export function changelogMarkdown(days: readonly ChangelogDay[] = CHANGELOG): string {
  const intro = [
    "# Journal des modifications",
    "",
    "Les nouveautés du connecteur MCP Assemblée nationale, de la plus récente à la plus ancienne.",
    `Le même journal est publié sur la landing : ${PUBLIC_SITE_URL}/nouveautes.`,
    "",
    "<!-- Fichier généré à partir de web/src/content/changelog.ts : modifier ce fichier, puis lancer `pnpm changelog` dans web/. -->",
  ];
  return [...intro, ...days.flatMap((day) => ["", dayMarkdown(day)])].join("\n") + "\n";
}
