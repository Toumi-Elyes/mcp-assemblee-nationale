import { CheckCircleIcon, XCircleIcon } from "@phosphor-icons/react/dist/ssr";
import { shownScrutins } from "@/lib/stats";
import { formatShortDay } from "@/lib/format";
import type { WeekData } from "@/lib/data/view-types";
import { Reveal } from "./reveal";
import { ScrutinRow } from "./scrutin-row";

const DOSSIERS_SHOWN = 6;
const SCRUTINS_PER_DOSSIER = 3;

export const WeekSection: React.FC<{ week: WeekData }> = ({ week }) => {
  const shown = week.groups.slice(0, DOSSIERS_SHOWN);
  const hidden = week.groups.length - shown.length;
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-2xl font-semibold">Cette semaine à l'Assemblée</h3>
        <p className="max-w-hero text-base text-muted">
          <span className="tabular font-mono font-semibold text-ink">{week.total}</span> scrutins du{" "}
          {formatShortDay(week.from)} au {formatShortDay(week.to)}, regroupés par dossier.
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {shown.map((group, index) => (
          <Reveal key={group.dossier?.key ?? "sans-dossier"} delay={(index % 2) * 100}>
            <article className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-raised p-2">
              <header className="flex flex-col gap-2 p-3">
                <h4 className="text-lg font-semibold">{group.dossier?.label ?? "Scrutins sans dossier rattaché"}</h4>
                <p className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
                  <span className="tabular">{group.scrutins.length} scrutins</span>
                  <span className="inline-flex items-center gap-1">
                    <CheckCircleIcon aria-hidden="true" size={16} weight="bold" />
                    {group.adopted} adoptés
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <XCircleIcon aria-hidden="true" size={16} weight="bold" />
                    {group.rejected} rejetés
                  </span>
                </p>
              </header>
              <ul className="flex flex-col gap-2">
                {shownScrutins(group, SCRUTINS_PER_DOSSIER).map((scrutin) => (
                  <ScrutinRow key={scrutin.uid} scrutin={scrutin} counts={week.counts.get(scrutin.uid)} />
                ))}
              </ul>
            </article>
          </Reveal>
        ))}
      </div>
      {hidden > 0 ? <p className="text-sm text-muted">Et {hidden} autres dossiers votés cette semaine.</p> : null}
    </div>
  );
};
