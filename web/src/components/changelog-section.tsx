import Link from "next/link";
import { CHANGELOG, HOME_CHANGES, latestChanges } from "@/content/changelog";
import { changelogDay } from "@/lib/changelog";
import { GITHUB_URL } from "@/lib/config";
import { LINK_TEXT } from "./button-styles";
import { ChangelogList } from "./changelog-list";
import { Section } from "./section";

export const ChangelogSection: React.FC = () => {
  const latest = CHANGELOG[0]?.date;
  return (
    <Section
      id="nouveautes"
      title="Nouveautés"
      intro="Ce que le connecteur sait faire de nouveau, jour après jour. Votre assistant en profite sans rien réinstaller."
      meta={
        <span className="flex flex-col gap-1">
          <Link href="/nouveautes" className={`${LINK_TEXT} font-medium`}>
            Tout le journal des nouveautés
          </Link>
          <a href={`${GITHUB_URL}/blob/main/CHANGELOG.md`} className={LINK_TEXT}>
            Le même journal sur GitHub
          </a>
          {latest !== undefined ? (
            <span>
              Dernière mise à jour le <time dateTime={latest}>{changelogDay(latest)}</time>
            </span>
          ) : null}
        </span>
      }
    >
      <ChangelogList days={latestChanges(HOME_CHANGES)} />
    </Section>
  );
};
