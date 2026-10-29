import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import type { Counts, VoteResult } from "@/lib/civix/types";
import { formatShortDay, formatNumber, pluralize } from "@/lib/format";
import { LINK_TEXT } from "./button-styles";
import { PositionBar } from "./position-bar";
import { ResultBadge } from "./result-badge";

type ScrutinRowData = { uid: string; date: string | null; title: string; result: VoteResult };

export const ScrutinRow: React.FC<{ scrutin: ScrutinRowData; counts: Counts | undefined }> = ({ scrutin, counts }) => {
  return (
    <li className="flex flex-col gap-2 rounded border border-line bg-bg p-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        {scrutin.date !== null ? (
          <time dateTime={scrutin.date} className="text-xs text-muted">
            {formatShortDay(scrutin.date)}
          </time>
        ) : null}
        <ResultBadge result={scrutin.result} />
        {counts !== undefined ? (
          <span className="tabular text-xs text-muted">
            {formatNumber(counts.pour)} pour, {formatNumber(counts.contre)} contre, {pluralize(counts.abstention, "abstention")}
          </span>
        ) : null}
      </div>
      <p className="text-base font-medium">{scrutin.title}</p>
      {counts !== undefined ? <PositionBar counts={counts} label="Répartition des votes" /> : null}
      <a href={`/scrutins/${scrutin.uid}`} className={`${LINK_TEXT} inline-flex items-center gap-1 self-start text-sm font-bold`}>
        Voir le scrutin
        <ArrowRightIcon aria-hidden="true" size={16} weight="bold" />
      </a>
    </li>
  );
};
