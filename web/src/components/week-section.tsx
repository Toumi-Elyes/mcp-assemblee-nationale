import Link from "next/link";
import type { Counts, Scrutin } from "@/lib/civix/types";
import { formatShortDay, formatNumber, pluralize } from "@/lib/format";
import { shownScrutins, type DossierGroup } from "@/lib/stats";
import { truncate } from "@/lib/text";
import { CountsText } from "./position-bar";
import { ResultBadge } from "./result-badge";
import { Section, Unavailable } from "./section";

const SCRUTINS_SHOWN_PER_DOSSIER = 3;
const TITLE_LIMIT = 170;
const LIST_LIMIT = 40;

export type WeekData = {
  from: string;
  to: string;
  total: number;
  groups: DossierGroup[];
  counts: Map<string, Counts>;
};

const ScrutinRow: React.FC<{ scrutin: Scrutin; counts: Counts | undefined }> = ({ scrutin, counts }) => {
  return (
    <li className="py-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        {scrutin.date !== null ? (
          <time dateTime={scrutin.date} className="text-xs text-muted">
            {formatShortDay(scrutin.date)}
          </time>
        ) : null}
        <ResultBadge result={scrutin.result} />
        {scrutin.isFinalVote ? (
          <span className="text-xs font-semibold text-muted">Vote sur l&apos;ensemble</span>
        ) : null}
      </div>
      <Link href={`/scrutins/${scrutin.uid}`} className="mt-1 block font-medium hover:underline">
        {truncate(scrutin.title, TITLE_LIMIT)}
      </Link>
      {counts ? (
        <p className="mt-1 text-sm text-muted">
          <CountsText counts={counts} />
        </p>
      ) : null}
    </li>
  );
};

const DossierCard: React.FC<{ group: DossierGroup; counts: Map<string, Counts> }> = ({ group, counts }) => {
  const shown = shownScrutins(group, SCRUTINS_SHOWN_PER_DOSSIER);
  const shownUids = new Set(shown.map((scrutin) => scrutin.uid));
  const others = group.scrutins
    .filter((scrutin) => !shownUids.has(scrutin.uid))
    .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? "") || (b.numero ?? 0) - (a.numero ?? 0));
  return (
    <article className="card p-5">
      <h3 className="text-lg font-semibold leading-snug">
        {group.dossier?.label ?? "Scrutins hors dossier législatif"}
      </h3>
      <p className="mt-1 text-sm text-muted">
        {pluralize(group.scrutins.length, "scrutin")} · {formatNumber(group.adopted)} adopté
        {group.adopted > 1 ? "s" : ""} · {formatNumber(group.rejected)} rejeté
        {group.rejected > 1 ? "s" : ""}
      </p>
      <ul className="mt-2 divide-y divide-line">
        {shown.map((scrutin) => (
          <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={counts.get(scrutin.uid)} />
        ))}
      </ul>
      {others.length > 0 ? (
        <details className="mt-2 text-sm">
          <summary className="cursor-pointer font-medium text-accent">
            Voir {others.length > 1 ? `les ${others.length} autres scrutins` : "l'autre scrutin"}
          </summary>
          <ul className="mt-2 divide-y divide-line">
            {others.slice(0, LIST_LIMIT).map((scrutin) => (
              <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={counts.get(scrutin.uid)} />
            ))}
          </ul>
          {others.length > LIST_LIMIT ? (
            <p className="mt-2 text-muted">
              Les {formatNumber(others.length - LIST_LIMIT)} suivants sont consultables sur{" "}
              <a className="link" href="https://www.civix.fr">
                CIVIX
              </a>
              .
            </p>
          ) : null}
        </details>
      ) : null}
    </article>
  );
};

export const WeekSection: React.FC<{ week: WeekData | null }> = ({ week }) => {
  return (
    <Section
      id="semaine"
      eyebrow="En direct"
      title="Cette semaine à l'Assemblée"
      intro={
        week
          ? `${pluralize(week.total, "scrutin")} du ${formatShortDay(week.from)} au ${formatShortDay(week.to)}, regroupés par texte. Chaque vote mène à sa page détaillée.`
          : undefined
      }
    >
      {week === null || week.groups.length === 0 ? (
        <Unavailable />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {week.groups.map((group) => (
            <DossierCard key={group.dossier?.key ?? "sans-dossier"} group={group} counts={week.counts} />
          ))}
        </div>
      )}
    </Section>
  );
};
