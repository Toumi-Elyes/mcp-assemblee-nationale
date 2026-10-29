import { ArrowSquareOutIcon } from "@phosphor-icons/react/dist/ssr";
import type { HeroChat } from "@/lib/data/view-types";
import { POSITION_LABELS, formatDay, formatNumber } from "@/lib/format";
import { LINK_TEXT } from "./button-styles";
import { PositionBar, PositionLegend } from "./position-bar";
import { ResultBadge } from "./result-badge";
import { Unavailable } from "./unavailable";

const UserTurn: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex flex-col items-end gap-1">
      <p className="font-display text-sm font-semibold uppercase tracking-wide text-muted">Vous</p>
      <p className="max-w-sm rounded-sm bg-surface px-3 py-2 text-base">{children}</p>
    </div>
  );
};

const AssistantTurn: React.FC<{ chat: HeroChat }> = ({ chat }) => {
  const { depute, counts, position, result, date } = chat;
  return (
    <div className="flex flex-col gap-3">
      <p className="font-display text-sm font-semibold uppercase tracking-wide text-muted">Votre assistant</p>
      <p className="text-base">
        {depute.fullName}
        {depute.groupAbbr !== null ? ` (${depute.groupAbbr})` : ""}, position enregistrée sur{" "}
        <a href={`/scrutins/${chat.scrutinUid}`} className={LINK_TEXT}>
          ce scrutin du {formatDay(date)}
        </a>{" "}
        : <strong className="font-bold">{POSITION_LABELS[position]}</strong>.
      </p>
      <div className="flex flex-col gap-3 border-l border-rule pl-4">
        <p className="text-sm text-ink-soft">{chat.scrutinTitle}</p>
        <span>
          <ResultBadge result={result} />
        </span>
        {counts !== null ? (
          <>
            <PositionBar counts={counts} label="Résultat du scrutin" />
            <PositionLegend counts={counts} />
            <p className="text-xs text-muted">
              {formatNumber(counts.total)} votants enregistrés. Chiffres officiels de l'Assemblée nationale.
            </p>
          </>
        ) : null}
      </div>
      <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <span className="text-muted">Sources :</span>
        {chat.assembleeUrl !== null ? (
          <a href={chat.assembleeUrl} className={`${LINK_TEXT} inline-flex items-center gap-1`}>
            Assemblée nationale <ArrowSquareOutIcon aria-hidden="true" size={16} />
          </a>
        ) : null}
        <a href={chat.civixUrl} className={`${LINK_TEXT} inline-flex items-center gap-1`}>
          CIVIX <ArrowSquareOutIcon aria-hidden="true" size={16} />
        </a>
      </p>
    </div>
  );
};

export const ChatExample: React.FC<{ chat: HeroChat | null; generatedAt: Date }> = ({ chat, generatedAt }) => {
  return (
    <figure className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between gap-4 border-b-2 border-rule pb-3">
        <p className="font-display text-xl font-semibold tracking-tight">Dans votre assistant</p>
        <p className="text-sm text-muted">Exemple</p>
      </div>
      <div className="flex flex-col gap-6">
        {chat !== null ? (
          <>
            <UserTurn>{chat.question}</UserTurn>
            <AssistantTurn chat={chat} />
          </>
        ) : (
          <>
            <UserTurn>Comment a voté mon député sur le dernier texte de loi ?</UserTurn>
            <Unavailable
              title="Exemple indisponible"
              detail="L'exemple se construit avec un vrai vote de l'Assemblée, et la source ne répond pas pour le moment."
            />
          </>
        )}
      </div>
      <figcaption className="border-t border-line pt-3 text-xs text-muted">
        {chat !== null
          ? `Illustration construite avec les données de l'Assemblée nationale lues le ${formatDay(
              generatedAt.toISOString().slice(0, 10),
            )}. Ce n'est pas une conversation enregistrée.`
          : "Illustration sans donnée : elle apparaît dès que la source répond."}
      </figcaption>
    </figure>
  );
};
