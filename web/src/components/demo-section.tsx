"use client";

import { useEffect, useRef, useState } from "react";
import { MagnifyingGlassIcon } from "@phosphor-icons/react";
import type { DemoAnswer } from "@/lib/data/demo";
import type { Depute, Position } from "@/lib/civix/types";
import type { DemoDepute } from "@/lib/data/view-types";
import { POSITION_LABELS, formatShortDay } from "@/lib/format";
import { cn } from "@/lib/cn";
import { BUTTON_PRIMARY, BUTTON_SECONDARY_SMALL, LINK_TEXT } from "./button-styles";
import { markProps, type MarkKey } from "./position-bar";
import { ResultBadge } from "./result-badge";
import { Section } from "./section";

type Suggestions = { topics: string[]; deputes: DemoDepute[] };

type Status = "idle" | "loading" | "done" | "error";

const SEARCH_DELAY_MS = 300;
const MIN_QUERY = 2;
const POSITION_MARK: Record<Position, MarkKey> = {
  pour: "pour",
  contre: "contre",
  abstention: "abstention",
  non_votant: "non_votant",
  unknown: "non_votant",
};

const Skeleton: React.FC = () => {
  return (
    <div aria-hidden="true" className="flex flex-col gap-3">
      {[0, 1, 2].map((item) => (
        <div key={item} className="rounded bg-surface p-4">
          <div className="skeleton h-4 w-1/4 rounded" />
          <div className="skeleton mt-3 h-4 w-full rounded" />
          <div className="skeleton mt-2 h-4 w-3/4 rounded" />
        </div>
      ))}
    </div>
  );
};

const Results: React.FC<{ answer: DemoAnswer }> = ({ answer }) => {
  if (answer.entries.length === 0) {
    return (
      <div className="flex flex-col gap-2 rounded bg-surface p-4">
        <p className="text-base font-bold">Aucun scrutin trouvé pour « {answer.topic} »</p>
        <p className="text-sm text-muted">
          Essayez un mot du titre officiel, par exemple « retraites » plutôt que le nom courant d'une réforme.
        </p>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-3">
      <p className="text-base">
        Position de <strong className="font-bold">{answer.depute.fullName}</strong>
        {answer.depute.groupAbbr !== null ? ` (${answer.depute.groupAbbr})` : ""} sur les {answer.entries.length}{" "}
        scrutins les plus pertinents pour « {answer.topic} »
        {answer.total !== null ? `, sur ${answer.total} au total` : ""}.
      </p>
      <ul className="flex flex-col gap-2">
        {answer.entries.map((entry) => (
          <li key={entry.uid} className="flex flex-col gap-2 rounded bg-surface p-4">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              {entry.date !== null ? (
                <time dateTime={entry.date} className="text-xs text-muted">
                  {formatShortDay(entry.date)}
                </time>
              ) : null}
              <ResultBadge result={entry.result} />
              <span className="inline-flex items-center gap-1 text-sm font-bold">
                <svg aria-hidden="true" viewBox="0 0 12 12" className="size-3">
                  <circle cx="6" cy="6" r="5.5" strokeWidth={1} className="stroke-ink-soft" {...markProps(POSITION_MARK[entry.position])} />
                </svg>
                {POSITION_LABELS[entry.position]}
              </span>
            </div>
            <a href={`/scrutins/${entry.uid}`} className={`${LINK_TEXT} text-base`}>
              {entry.title}
            </a>
            <p className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
              {entry.assembleeUrl !== null ? (
                <a href={entry.assembleeUrl} className={LINK_TEXT}>
                  Source Assemblée nationale
                </a>
              ) : null}
              <a href={entry.civixUrl} className={LINK_TEXT}>
                Source CIVIX
              </a>
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export const DemoSection: React.FC<{ suggestions: Suggestions }> = ({ suggestions }) => {
  const [query, setQuery] = useState("");
  const [candidates, setCandidates] = useState<Depute[]>([]);
  const [searching, setSearching] = useState(false);
  const [listOpen, setListOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [selected, setSelected] = useState<DemoDepute | null>(null);
  const [topic, setTopic] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [answer, setAnswer] = useState<DemoAnswer | null>(null);
  const [message, setMessage] = useState("");
  const [fieldError, setFieldError] = useState<{ depute?: string; topic?: string }>({});
  const timer = useRef<number | undefined>(undefined);
  const controller = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      window.clearTimeout(timer.current);
      controller.current?.abort();
    };
  }, []);

  const onQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);
    setSelected(null);
    setActiveIndex(-1);
    window.clearTimeout(timer.current);
    controller.current?.abort();
    if (value.trim().length < MIN_QUERY) {
      setCandidates([]);
      setListOpen(false);
      setSearching(false);
      return;
    }
    setSearching(true);
    timer.current = window.setTimeout(async () => {
      const current = new AbortController();
      controller.current = current;
      try {
        const response = await fetch(`/api/deputes?q=${encodeURIComponent(value.trim())}`, { signal: current.signal });
        const payload: unknown = await response.json();
        const list =
          response.ok && typeof payload === "object" && payload !== null && "deputes" in payload && Array.isArray(payload.deputes)
            ? (payload.deputes as Depute[])
            : [];
        setCandidates(list);
        setListOpen(true);
        setSearching(false);
      } catch {
        if (!current.signal.aborted) {
          setCandidates([]);
          setSearching(false);
          setFieldError((previous) => ({ ...previous, depute: "La recherche de députés est momentanément indisponible." }));
        }
      }
    }, SEARCH_DELAY_MS);
  };

  const pick = (depute: DemoDepute) => {
    setSelected(depute);
    setQuery(depute.fullName);
    setListOpen(false);
    setCandidates([]);
    setFieldError((previous) => ({ ...previous, depute: undefined }));
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (!listOpen || candidates.length === 0) {
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((index) => (index + 1) % candidates.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((index) => (index <= 0 ? candidates.length - 1 : index - 1));
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      const chosen = candidates[activeIndex];
      if (chosen !== undefined) {
        pick(chosen);
      }
    } else if (event.key === "Escape") {
      setListOpen(false);
    }
  };

  const run = async (depute: DemoDepute, subject: string) => {
    setStatus("loading");
    setAnswer(null);
    try {
      const response = await fetch(
        `/api/demo?depute=${encodeURIComponent(depute.uid)}&sujet=${encodeURIComponent(subject)}`,
      );
      const payload: unknown = await response.json();
      if (!response.ok) {
        const text =
          typeof payload === "object" && payload !== null && "error" in payload && typeof payload.error === "string"
            ? payload.error
            : "Données momentanément indisponibles.";
        setMessage(text);
        setStatus("error");
        return;
      }
      setAnswer(payload as DemoAnswer);
      setStatus("done");
    } catch {
      setMessage("Données momentanément indisponibles. Réessayez dans quelques minutes.");
      setStatus("error");
    }
  };

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const errors: { depute?: string; topic?: string } = {};
    if (selected === null) {
      errors.depute = "Choisissez un député dans la liste de suggestions.";
    }
    if (topic.trim().length < MIN_QUERY) {
      errors.topic = "Indiquez un sujet d'au moins 2 lettres, par exemple « budget ».";
    }
    setFieldError(errors);
    if (selected === null || errors.topic !== undefined) {
      return;
    }
    void run(selected, topic.trim());
  };

  const onSuggestedDeputy = (depute: DemoDepute) => () => {
    pick(depute);
  };
  const onSuggestedTopic = (value: string) => () => {
    setTopic(value);
    setFieldError((previous) => ({ ...previous, topic: undefined }));
  };

  return (
    <Section
      id="demo"
      eyebrow="Essayez maintenant"
      title="Comment a voté un député sur un sujet ?"
      intro="C'est la question que votre assistant se pose en coulisses. Choisissez un député et un sujet : les résultats viennent des mêmes données, avec le lien de chaque source."
    >
      <div className="grid gap-8 lg:grid-cols-5">
        <form onSubmit={onSubmit} noValidate className="flex flex-col gap-6 lg:col-span-2">
          <div className="relative flex flex-col gap-2">
            <label htmlFor="demo-depute" className="text-sm font-bold">
              Député
            </label>
            <div className="relative">
              <MagnifyingGlassIcon aria-hidden="true" size={20} className="pointer-events-none absolute left-3 top-3 text-muted" />
              <input
                id="demo-depute"
                role="combobox"
                aria-expanded={listOpen}
                aria-controls="demo-depute-liste"
                aria-autocomplete="list"
                aria-describedby={fieldError.depute !== undefined ? "demo-depute-erreur" : undefined}
                aria-invalid={fieldError.depute !== undefined}
                autoComplete="off"
                value={query}
                onChange={onQueryChange}
                onKeyDown={onKeyDown}
                placeholder="Commencez à taper un nom"
                className="w-full rounded border border-line bg-raised py-2 pl-10 pr-3 text-base transition hover:bg-hover"
              />
            </div>
            {listOpen ? (
              <ul
                id="demo-depute-liste"
                role="listbox"
                aria-label="Députés correspondants"
                className="absolute inset-x-0 top-20 z-10 flex listbox-height flex-col gap-1 overflow-auto rounded-lg border border-line bg-raised p-1"
              >
                {candidates.length === 0 ? (
                  <li className="px-3 py-2 text-sm text-muted">Aucun député ne correspond à cette recherche.</li>
                ) : (
                  candidates.map((candidate, index) => (
                    <li
                      key={candidate.uid}
                      role="option"
                      aria-selected={index === activeIndex}
                      onClick={() => {
                        pick(candidate);
                      }}
                      className={cn(
                        "cursor-pointer rounded px-3 py-2 text-sm transition hover:bg-hover",
                        index === activeIndex ? "bg-hover" : undefined,
                      )}
                    >
                      <span className="font-bold">{candidate.fullName}</span>
                      <span className="text-muted">
                        {candidate.groupAbbr !== null ? ` ${candidate.groupAbbr}` : ""}
                        {candidate.department !== null ? `, ${candidate.department}` : ""}
                      </span>
                    </li>
                  ))
                )}
              </ul>
            ) : null}
            <p className="min-h-6 text-sm text-muted" aria-live="polite">
              {searching ? "Recherche en cours" : null}
            </p>
            {fieldError.depute !== undefined ? (
              <p id="demo-depute-erreur" className="text-sm font-bold">
                {fieldError.depute}
              </p>
            ) : null}
            {suggestions.deputes.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {suggestions.deputes.map((depute) => (
                  <button key={depute.uid} type="button" onClick={onSuggestedDeputy(depute)} className={BUTTON_SECONDARY_SMALL}>
                    {depute.fullName}
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="demo-sujet" className="text-sm font-bold">
              Sujet
            </label>
            <input
              id="demo-sujet"
              value={topic}
              onChange={(event) => {
                setTopic(event.target.value);
              }}
              aria-describedby={fieldError.topic !== undefined ? "demo-sujet-erreur" : undefined}
              aria-invalid={fieldError.topic !== undefined}
              maxLength={80}
              placeholder="Par exemple : budget, retraites, logement"
              className="rounded border border-line bg-raised px-3 py-2 text-base transition hover:bg-hover"
            />
            {fieldError.topic !== undefined ? (
              <p id="demo-sujet-erreur" className="text-sm font-bold">
                {fieldError.topic}
              </p>
            ) : null}
            {suggestions.topics.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {suggestions.topics.map((value) => (
                  <button key={value} type="button" onClick={onSuggestedTopic(value)} className={BUTTON_SECONDARY_SMALL}>
                    {value.length > 48 ? `${value.slice(0, 47)}…` : value}
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          <button type="submit" disabled={status === "loading"} className={`${BUTTON_PRIMARY} self-start disabled:opacity-50`}>
            Voir les votes
          </button>
        </form>

        <div className="flex flex-col gap-3 lg:col-span-3" aria-live="polite" aria-busy={status === "loading"}>
          {status === "idle" ? (
            <div className="flex h-full flex-col justify-center gap-2 rounded-lg border border-line bg-surface p-6">
              <p className="text-lg font-bold">Les résultats apparaissent ici</p>
              <p className="text-base text-muted">
                Choisissez un député dans les suggestions ou tapez son nom, ajoutez un sujet, puis lancez la recherche.
              </p>
            </div>
          ) : null}
          {status === "loading" ? <Skeleton /> : null}
          {status === "error" ? (
            <div role="alert" className="flex flex-col gap-2 rounded-lg border border-line bg-surface p-6">
              <p className="text-lg font-bold">La recherche n'a pas abouti</p>
              <p className="text-base text-muted">{message}</p>
            </div>
          ) : null}
          {status === "done" && answer !== null ? <Results answer={answer} /> : null}
        </div>
      </div>
    </Section>
  );
};
