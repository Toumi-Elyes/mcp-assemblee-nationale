import type { Counts, VoteResult } from "@/lib/civix/types";
import { formatNumber, formatShortDay, pluralize } from "@/lib/format";
import { PositionBar } from "./position-bar";
import { ResultBadge } from "./result-badge";

type ScrutinRowData = { uid: string; date: string | null; title: string; result: VoteResult };

const BOARD_COLUMNS = "sm:grid sm:grid-cols-[4.5rem_minmax(0,1fr)_6.5rem] sm:gap-x-5";

export const BoardHead: React.FC = () => {
  return (
    <div
      aria-hidden="true"
      className={`hidden border-b border-line pb-1.5 font-display text-sm font-semibold uppercase tracking-wide text-muted ${BOARD_COLUMNS}`}
    >
      <span>Date</span>
      <span>Scrutin</span>
      <span className="text-right">Résultat</span>
    </div>
  );
};

export const ScrutinRow: React.FC<{ scrutin: ScrutinRowData; counts: Counts | undefined }> = ({ scrutin, counts }) => {
  return (
    <li className={`flex flex-col gap-2 border-b border-line py-3.5 ${BOARD_COLUMNS} sm:items-start`}>
      <span className="flex items-center justify-between gap-3 sm:contents">
        {scrutin.date !== null ? (
          <time dateTime={scrutin.date} className="tabular font-display text-lg font-semibold leading-6">
            {formatShortDay(scrutin.date)}
          </time>
        ) : (
          <span className="text-sm text-muted">Date inconnue</span>
        )}
        <span className="sm:order-3 sm:justify-self-end">
          <ResultBadge result={scrutin.result} />
        </span>
      </span>
      <span className="flex min-w-0 flex-col gap-2 sm:order-2">
        <a
          href={`/scrutins/${scrutin.uid}`}
          className="text-base font-medium leading-6 text-ink underline decoration-line hover:text-accent hover:decoration-accent"
        >
          {scrutin.title}
        </a>
        {counts !== undefined ? (
          <span className="flex flex-col gap-1.5">
            <PositionBar counts={counts} label="Répartition des votes" />
            <span className="tabular text-sm text-ink-soft">
              {formatNumber(counts.pour)} pour · {formatNumber(counts.contre)} contre ·{" "}
              {pluralize(counts.abstention, "abstention")}
            </span>
          </span>
        ) : null}
      </span>
    </li>
  );
};
