"use client";

import { useEffect, useRef, useState } from "react";
import { MagnifyingGlassIcon } from "@phosphor-icons/react";
import type { DemoAnswer } from "@/lib/data/demo";
import type { Depute, Position } from "@/lib/civix/types";
import type { DemoDepute } from "@/lib/data/view-types";
import { POSITION_LABELS, formatDay } from "@/lib/format";
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
    <div aria-hidden="true" className="flex flex-col">
      {[0, 1, 2].map((item) => (
        <div key={item} className="flex flex-col gap-2 border-b border-line py-4">
          <div className="skeleton h-4 w-1/5" />
          <div className="skeleton h-4 w-full" />
          <div className="skeleton h-4 w-2/3" />
        </div>
      ))}
    </div>
  );
};

const NO_RECORD_LABEL = "Aucun vote enregistré";

const PositionMark: React.FC<{ position: Position }> = ({ position }) => {
  if (position === "unknown") {
    return (
      <span className="inline-flex items-center gap-1.5 font-display text-base font-semibold text-muted">
        <svg aria-hidden="true" viewBox="0 0 12 12" className="size-3.5">
          <circle cx="6" cy="6" r="5" strokeWidth={1} strokeDasharray="2 2" fill="none" className="stroke-muted" />
        </svg>
        {NO_RECORD_LABEL}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 font-display text-base font-semibold">
      <svg aria-hidden="true" viewBox="0 0 12 12" className="size-3.5">
        <circle cx="6" cy="6" r="5.5" strokeWidth={1} className="stroke-ink-soft" {...markProps(POSITION_MARK[position])} />
      </svg>
      {POSITION_LABELS[position]}
    </span>
  );
};

const Results: React.FC<{ answer: DemoAnswer }> = ({ answer }) => {
  if (answer.entries.length === 0) {
    return (
      <div className="flex flex-col gap-2 border-y border-line py-5">
        <p className="text-lg font-bold">Aucun scrutin trouvé pour « {answer.topic} »</p>
        <p className="text-base text-ink-soft">
          Essayez un mot du titre officiel, par exemple « retraites » plutôt que le nom courant d'une réforme.
        </p>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-4">
      <p className="max-w-measure text-base text-ink-soft">
        Position de <strong className="font-bold text-ink">{answer.depute.fullName}</strong>
        {answer.depute.groupAbbr !== null ? ` (${answer.depute.groupAbbr})` : ""} sur les {answer.entries.length}{" "}
        scrutins les plus pertinents pour « {answer.topic} »
        {answer.total !== null ? `, sur ${answer.total} au total` : ""}.
      </p>
      <ul className="flex flex-col border-t-2 border-rule">
        {answer.entries.map((entry) => (
          <li
            key={entry.uid}
            className="flex flex-col gap-2 border-b border-line py-4 sm:grid sm:grid-cols-[7rem_minmax(0,1fr)_11rem] sm:gap-x-6"
          >
            <span className="flex flex-wrap items-center gap-3 sm:contents">
              {entry.date !== null ? (
                <time dateTime={entry.date} className="tabular font-display text-base font-semibold">
                  {formatDay(entry.date)}
                </time>
              ) : (
                <span className="text-sm text-muted">Date inconnue</span>
              )}
              <span className="sm:order-3">
                <PositionMark position={entry.position} />
              </span>
            </span>
            <span className="flex min-w-0 flex-col gap-2 sm:order-2">
              <a href={`/scrutins/${entry.uid}`} className="text-base font-medium text-ink underline decoration-line hover:text-accent hover:decoration-accent">
                {entry.title}
              </a>
              <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <ResultBadge result={entry.result} />
                {entry.assembleeUrl !== null ? (
                  <a href={entry.assembleeUrl} className={LINK_TEXT}>
                    Source Assemblée nationale
                  </a>
                ) : null}
                <a href={entry.civixUrl} className={LINK_TEXT}>
                  Source CIVIX
                </a>
              </span>
            </span>
          </li>
        ))}
      </ul>
      {answer.entries.some((entry) => entry.position === "unknown") ? (
        <p className="max-w-measure text-sm text-ink-soft">
          «&nbsp;{NO_RECORD_LABEL}&nbsp;» : la liste des votes de ce scrutin ne contient pas cette personne, par exemple
          parce qu'elle n'était pas encore élue à cette date.
        </p>
      ) : null}
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

  const blankClass =
    "w-full border-0 border-b-2 border-rule bg-transparent px-1 py-1 font-display text-2xl font-semibold text-ink placeholder:font-normal placeholder:text-muted transition-colors hover:border-accent focus:border-accent focus:outline-none sm:text-3xl";

  return (
    <Section
      id="demo"
      title="Comment a voté un député sur un sujet ?"
      intro="C'est la question que votre assistant se pose en coulisses. Choisissez un député et un sujet : les résultats viennent des mêmes données, avec le lien de chaque source."
    >
      <div className="flex flex-col gap-10">
        <form onSubmit={onSubmit} noValidate className="flex flex-col gap-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:flex-wrap lg:items-end lg:gap-x-4">
            <span aria-hidden="true" className="font-display text-2xl font-semibold text-ink-soft sm:text-3xl lg:pb-2">
              Comment a voté
            </span>
            <div className="relative flex flex-col gap-1 lg:w-96">
              <label htmlFor="demo-depute" className="text-sm font-bold text-ink-soft">
                Député
              </label>
              <div className="relative">
                <MagnifyingGlassIcon aria-hidden="true" size={22} className="pointer-events-none absolute left-1 top-3 text-muted" />
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
                  placeholder="un nom"
                  className={`${blankClass} pl-8`}
                />
              </div>
              {listOpen ? (
                <ul
                  id="demo-depute-liste"
                  role="listbox"
                  aria-label="Députés correspondants"
                  className="absolute inset-x-0 top-full z-10 mt-1 flex listbox-height flex-col overflow-auto border border-rule bg-raised shadow-lg shadow-black/10"
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
                          "cursor-pointer border-b border-line px-3 py-2 text-sm transition-colors last:border-b-0 hover:bg-hover",
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
            </div>
            <span aria-hidden="true" className="font-display text-2xl font-semibold text-ink-soft sm:text-3xl lg:pb-2">
              sur
            </span>
            <div className="flex flex-col gap-1 lg:w-80">
              <label htmlFor="demo-sujet" className="text-sm font-bold text-ink-soft">
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
                placeholder="budget, retraites…"
                className={blankClass}
              />
            </div>
            <span aria-hidden="true" className="hidden font-display text-3xl font-semibold text-ink-soft lg:block lg:pb-2">
              ?
            </span>
            <button
              type="submit"
              disabled={status === "loading"}
              className={`${BUTTON_PRIMARY} self-start disabled:opacity-50 lg:mb-1 lg:ml-4 lg:self-end`}
            >
              Voir les votes
            </button>
          </div>

          <p className="min-h-5 text-sm text-muted" aria-live="polite">
            {searching ? "Recherche en cours" : null}
          </p>
          {fieldError.depute !== undefined ? (
            <p id="demo-depute-erreur" className="-mt-4 text-sm font-bold">
              {fieldError.depute}
            </p>
          ) : null}
          {fieldError.topic !== undefined ? (
            <p id="demo-sujet-erreur" className="-mt-4 text-sm font-bold">
              {fieldError.topic}
            </p>
          ) : null}

          <div className="grid gap-4 border-t border-line pt-4 md:grid-cols-2">
            {suggestions.deputes.length > 0 ? (
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted">Députés suggérés</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.deputes.map((depute) => (
                    <button key={depute.uid} type="button" onClick={onSuggestedDeputy(depute)} className={BUTTON_SECONDARY_SMALL}>
                      {depute.fullName}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
            {suggestions.topics.length > 0 ? (
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted">Dossiers récemment votés</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.topics.map((value) => (
                    <button key={value} type="button" onClick={onSuggestedTopic(value)} className={BUTTON_SECONDARY_SMALL}>
                      {value.length > 48 ? `${value.slice(0, 47)}…` : value}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </form>

        <div className="flex flex-col gap-3" aria-live="polite" aria-busy={status === "loading"}>
          {status === "idle" ? (
            <p className="border-y border-line py-5 text-base text-ink-soft">
              Les résultats apparaissent ici. Choisissez un député dans les suggestions ou tapez son nom, ajoutez un
              sujet, puis lancez la recherche.
            </p>
          ) : null}
          {status === "loading" ? <Skeleton /> : null}
          {status === "error" ? (
            <div role="alert" className="flex flex-col gap-2 border-y border-line py-5">
              <p className="text-lg font-bold">La recherche n'a pas abouti</p>
              <p className="text-base text-ink-soft">{message}</p>
            </div>
          ) : null}
          {status === "done" && answer !== null ? <Results answer={answer} /> : null}
        </div>
      </div>
    </Section>
  );
};
