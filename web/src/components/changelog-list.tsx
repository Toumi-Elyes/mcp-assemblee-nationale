import { CHANGE_LABELS, type ChangelogDay, type ChangeKind } from "@/content/changelog";
import { changelogDay, pullRequestUrl } from "@/lib/changelog";
import { cn } from "@/lib/cn";
import { LINK_TEXT } from "./button-styles";

const KIND_STYLES: Readonly<Record<ChangeKind, string>> = {
  nouveau: "border-accent bg-accent text-on-accent",
  amelioration: "border-accent text-accent",
  correction: "border-line text-ink-soft",
};

type ChangelogListProps = { days: readonly ChangelogDay[]; headingLevel?: "h2" | "h3" };

export const ChangelogList: React.FC<ChangelogListProps> = ({ days, headingLevel = "h3" }) => {
  const Heading = headingLevel;
  return (
    <ol className="flex flex-col gap-10">
      {days.map((day) => (
        <li key={day.date} className="grid gap-4 lg:grid-cols-12 lg:gap-12">
          <Heading className="font-display text-2xl font-semibold tracking-tight lg:col-span-3">
            <time dateTime={day.date}>{changelogDay(day.date)}</time>
          </Heading>
          <ul className="border-t-2 border-rule lg:col-span-9">
            {day.changes.map((change) => (
              <li key={change.pr} className="flex flex-col gap-2 border-b border-line py-4 sm:flex-row sm:gap-6">
                <span
                  className={cn(
                    "h-fit w-fit shrink-0 rounded-sm border px-2 py-0.5 text-xs font-bold sm:w-24 sm:text-center",
                    KIND_STYLES[change.kind],
                  )}
                >
                  {CHANGE_LABELS[change.kind]}
                </span>
                <div className="flex flex-col gap-1">
                  <p className="font-display text-xl font-semibold leading-snug">{change.title}</p>
                  <p className="max-w-measure text-base text-ink-soft text-pretty">
                    {change.detail}{" "}
                    <a href={pullRequestUrl(change.pr)} className={cn(LINK_TEXT, "text-sm")}>
                      #{change.pr}
                    </a>
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ol>
  );
};
