import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import type { HeroChat } from "@/lib/data/view-types";
import { POSITION_LABELS, formatDay } from "@/lib/format";
import { LINK_TEXT } from "./button-styles";
import { Unavailable } from "./unavailable";

const Speaker: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <p className="font-display text-sm font-semibold uppercase tracking-wide text-muted">{children}</p>;
};

export const ChatExample: React.FC<{ chat: HeroChat | null; generatedAt: Date }> = ({ chat, generatedAt }) => {
  return (
    <figure className="flex flex-col gap-5">
      <p className="border-b-2 border-rule pb-3 font-display text-xl font-semibold tracking-tight">
        Et dans votre assistant
      </p>
      <div className="flex flex-col items-end gap-1">
        <Speaker>Vous</Speaker>
        <p className="max-w-sm rounded-sm bg-surface px-3 py-2 text-base">
          {chat !== null ? chat.question : "Comment a voté mon député sur le dernier texte de loi ?"}
        </p>
      </div>
      {chat !== null ? (
        <div className="flex flex-col gap-2">
          <Speaker>Votre assistant</Speaker>
          <p className="text-base">
            {chat.depute.fullName}
            {chat.depute.groupAbbr !== null ? ` (${chat.depute.groupAbbr})` : ""} : «&nbsp;
            <strong className="font-bold">{POSITION_LABELS[chat.position]}</strong>&nbsp;» sur ce texte, voté le{" "}
            {formatDay(chat.date)}.
          </p>
          <p title={chat.scrutinTitle} className="line-clamp-2 text-sm text-ink-soft">
            {chat.scrutinTitle}
          </p>
          <a href={`/scrutins/${chat.scrutinUid}`} className={`${LINK_TEXT} self-start text-base font-medium`}>
            Voir le scrutin et ses sources{" "}
            <ArrowRightIcon aria-hidden="true" size={14} weight="bold" className="inline" />
          </a>
        </div>
      ) : (
        <Unavailable
          title="Exemple indisponible"
          detail="L'exemple utilise un vrai vote de l'Assemblée, et la source ne répond pas pour le moment."
        />
      )}
      <figcaption className="border-t border-line pt-3 text-xs text-muted">
        {chat !== null
          ? `Exemple construit avec les données lues le ${formatDay(generatedAt.toISOString().slice(0, 10))}, pas une conversation enregistrée.`
          : "L'exemple apparaît dès que la source répond."}
      </figcaption>
    </figure>
  );
};
