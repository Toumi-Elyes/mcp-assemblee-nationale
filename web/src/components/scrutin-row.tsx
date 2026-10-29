import type { Counts, Scrutin } from "@/lib/civix/types";
import { formatShortDay, formatNumber } from "@/lib/format";
import { LINK_TEXT } from "./button-styles";
import { PositionBar } from "./position-bar";
import { ResultBadge } from "./result-badge";

export const ScrutinRow: React.FC<{ scrutin: Scrutin; counts: Counts | undefined }> = ({ scrutin, counts }) => {
  return (
    <li className="flex flex-col gap-2 rounded-lg bg-surface p-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        {scrutin.date !== null ? (
          <time dateTime={scrutin.date} className="text-xs text-muted">
            {formatShortDay(scrutin.date)}
          </time>
        ) : null}
        <ResultBadge result={scrutin.result} />
        {counts !== undefined ? (
          <span className="tabular font-mono text-xs text-muted">
            {formatNumber(counts.pour)} pour, {formatNumber(counts.contre)} contre, {formatNumber(counts.abstention)} abst.
          </span>
        ) : null}
      </div>
      <a href={`/scrutins/${scrutin.uid}`} className={`${LINK_TEXT} text-base`}>
        {scrutin.title}
      </a>
      {counts !== undefined ? <PositionBar counts={counts} label="Répartition des votes" /> : null}
    </li>
  );
};
