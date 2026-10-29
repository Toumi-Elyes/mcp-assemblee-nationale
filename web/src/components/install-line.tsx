import { ArrowDownIcon } from "@phosphor-icons/react/dist/ssr";
import { CTA_LABEL, INSTALL_HREF } from "@/lib/config";
import { cn } from "@/lib/cn";
import { LINK_TEXT } from "./button-styles";
import { CopyField } from "./copy-field";

const STOPS = [
  {
    title: "Copiez l'adresse",
    text: "Un bouton la copie pour vous. C'est l'adresse du connecteur, rien d'autre.",
  },
  {
    title: "Collez l'adresse dans votre assistant",
    text: "Dans les réglages des connecteurs de Claude ou de ChatGPT, ajoutez un connecteur personnalisé.",
  },
  {
    title: "Posez votre question",
    text: "En français, comme à une personne\u00a0: «\u00a0Comment a voté ma députée sur le budget\u00a0?\u00a0»",
  },
] as const;

type InstallLineProps = { fieldId: string; headingId: string; className?: string };

export const InstallLine: React.FC<InstallLineProps> = ({ fieldId, headingId, className }) => {
  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-6">
        <h2 id={headingId} className="font-display text-2xl font-semibold tracking-tight">
          {CTA_LABEL} : trois étapes, aucune ligne de code
        </h2>
        <p className="text-sm text-ink-soft">Gratuit, sans compte, sans clé. Pour Claude et ChatGPT.</p>
      </div>
      <ol className="grid gap-0 lg:grid-cols-[minmax(0,8fr)_minmax(0,5fr)_minmax(0,5fr)]">
        {STOPS.map((stop, index) => {
          const isFirst = index === 0;
          const isLast = index === STOPS.length - 1;
          return (
            <li key={stop.title} className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 lg:flex lg:flex-col lg:gap-2">
              <div aria-hidden="true" className="flex flex-col items-center lg:flex-row">
                <span
                  className={cn(
                    "grid size-7 shrink-0 place-items-center rounded-full border-2 border-rule font-display text-sm font-bold",
                    isFirst ? "bg-rule text-bg" : "bg-bg text-ink",
                  )}
                >
                  {index + 1}
                </span>
                <span className={cn("w-0.5 flex-1 bg-rule lg:h-0.5 lg:w-auto", isLast ? "max-lg:hidden lg:bg-line" : undefined)} />
              </div>
              <div className={cn("flex flex-col gap-1.5 pb-8 lg:pb-0", isLast ? "pb-0" : "lg:pr-8")}>
                <h3 className="font-display text-xl font-semibold leading-tight">
                  <span className="sr-only">Étape {index + 1} : </span>
                  {stop.title}
                </h3>
                <p className="max-w-measure text-base text-ink-soft">{stop.text}</p>
                {isFirst ? <CopyField id={fieldId} className="mt-1" /> : null}
                {index === 1 ? (
                  <a href={INSTALL_HREF} className={`${LINK_TEXT} self-start text-base font-medium`}>
                    Étapes détaillées pour chaque{" "}
                    <span className="whitespace-nowrap">
                      assistant <ArrowDownIcon aria-hidden="true" size={16} weight="bold" className="inline" />
                    </span>
                  </a>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
      <p className="max-w-measure text-sm text-muted">
        Un connecteur est une adresse que votre assistant sait interroger pour obtenir des données fiables. Son nom
        technique est MCP.
      </p>
    </div>
  );
};
