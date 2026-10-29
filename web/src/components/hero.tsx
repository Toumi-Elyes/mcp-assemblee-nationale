import { ArrowDown } from "lucide-react";
import { MCP_URL } from "@/lib/config";
import { formatDay, formatNumber } from "@/lib/format";
import { CopyButton } from "./copy-button";

export type HeroCounters = {
  legislature: number | null;
  scrutins: number | null;
  latestDate: string | null;
  deputes: number | null;
  groupes: number | null;
};

const Counter: React.FC<{ value: string; label: string }> = ({ value, label }) => {
  return (
    <div className="card px-4 py-3">
      <dd className="font-serif text-2xl font-semibold tabular-nums sm:text-3xl">{value}</dd>
      <dt className="text-sm text-muted">{label}</dt>
    </div>
  );
};

export const Hero: React.FC<{ counters: HeroCounters | null }> = ({ counters }) => {
  const legislature = counters?.legislature;
  return (
    <div className="mx-auto w-full max-w-6xl px-4 pb-8 pt-12 sm:px-6 sm:pt-20">
      <p className="eyebrow mb-4">Données ouvertes de l&apos;Assemblée nationale</p>
      <h1 className="max-w-4xl text-4xl font-semibold leading-tight sm:text-6xl">
        Demandez à votre IA comment votent vos députés
      </h1>
      <p className="mt-5 max-w-2xl text-lg text-muted">
        Ce connecteur branche Claude, ChatGPT ou Gemini sur les votes réels de l&apos;Assemblée.
        L&apos;IA va chercher les chiffres au lieu de répondre de mémoire, et cite la source de chaque
        scrutin. Gratuit, sans compte.
      </p>

      <div className="mt-8 max-w-2xl">
        <label htmlFor="mcp-url" className="mb-2 block text-sm font-semibold">
          L&apos;adresse à coller dans votre assistant
        </label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            id="mcp-url"
            readOnly
            value={MCP_URL}
            className="card min-w-0 flex-1 px-3 py-2.5 font-mono text-sm"
          />
          <CopyButton value={MCP_URL} label="Copier l'adresse" className="justify-center" />
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <a href="#installer-claude" className="btn btn-primary">
            Ajouter à Claude
          </a>
          <a href="#installer-chatgpt" className="btn">
            Ajouter à ChatGPT
          </a>
          <a href="#semaine" className="btn border-transparent bg-transparent text-muted">
            <ArrowDown aria-hidden className="size-4" />
            Voir les données du moment
          </a>
        </div>
      </div>

      <dl className="mt-12 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Chiffres du moment">
        <Counter
          value={counters?.scrutins !== null && counters?.scrutins !== undefined ? formatNumber(counters.scrutins) : "—"}
          label={
            legislature !== null && legislature !== undefined
              ? `scrutins en ${legislature}e législature`
              : "scrutins dans la législature en cours"
          }
        />
        <Counter
          value={counters?.latestDate !== null && counters?.latestDate !== undefined ? formatDay(counters.latestDate) : "—"}
          label="date du dernier vote"
        />
        <Counter
          value={counters?.deputes !== null && counters?.deputes !== undefined ? formatNumber(counters.deputes) : "—"}
          label="députés en exercice"
        />
        <Counter
          value={counters?.groupes !== null && counters?.groupes !== undefined ? formatNumber(counters.groupes) : "—"}
          label="groupes parlementaires"
        />
      </dl>
    </div>
  );
};
