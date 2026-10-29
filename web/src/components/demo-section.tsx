"use client";

import { ExternalLink, Search } from "lucide-react";
import { useRef, useState } from "react";
import { Section } from "./section";
import { ResultBadge } from "./result-badge";
import { formatDay, POSITION_LABELS } from "@/lib/format";
import type { Position, VoteResult } from "@/lib/civix/types";

export type DemoDepute = {
  uid: string;
  fullName: string;
  groupAbbr: string | null;
  department: string | null;
};

type DemoEntry = {
  uid: string;
  date: string | null;
  title: string;
  dossier: string | null;
  result: VoteResult;
  position: Position;
  civixUrl: string;
  assembleeUrl: string | null;
};

type DemoAnswer = {
  depute: DemoDepute & { civixUrl: string; assembleeUrl: string };
  topic: string;
  total: number | null;
  entries: DemoEntry[];
};

type Status = "idle" | "loading" | "error";

const SEARCH_DELAY_MS = 250;
const MIN_QUERY_LENGTH = 2;
const GENERIC_ERROR = "Données momentanément indisponibles. Réessayez dans quelques minutes.";

type DemoProps = { topics: string[]; deputes: DemoDepute[] };

const describeDepute = (depute: DemoDepute): string => {
  const parts = [depute.groupAbbr, depute.department].filter((part): part is string => part !== null);
  return parts.join(" · ");
};

export const DemoSection: React.FC<DemoProps> = ({ topics, deputes }) => {
  const [query, setQuery] = useState("");
  const [candidates, setCandidates] = useState<DemoDepute[]>([]);
  const [selected, setSelected] = useState<DemoDepute | null>(null);
  const [topic, setTopic] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [answer, setAnswer] = useState<DemoAnswer | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const searchCounter = useRef(0);

  const runSearch = async (text: string, ticket: number) => {
    try {
      const response = await fetch(`/api/deputes?q=${encodeURIComponent(text)}`);
      if (!response.ok) {
        throw new Error("search failed");
      }
      const payload: { deputes: DemoDepute[] } = await response.json();
      if (ticket === searchCounter.current) {
        setCandidates(payload.deputes);
      }
    } catch {
      if (ticket === searchCounter.current) {
        setCandidates([]);
        setMessage(GENERIC_ERROR);
      }
    }
  };

  const onQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const text = event.target.value;
    setQuery(text);
    setSelected(null);
    setMessage(null);
    searchCounter.current += 1;
    const ticket = searchCounter.current;
    if (timer.current !== null) {
      clearTimeout(timer.current);
    }
    if (text.trim().length < MIN_QUERY_LENGTH) {
      setCandidates([]);
      return;
    }
    timer.current = setTimeout(() => {
      void runSearch(text.trim(), ticket);
    }, SEARCH_DELAY_MS);
  };

  const choose = (depute: DemoDepute) => {
    searchCounter.current += 1;
    setSelected(depute);
    setQuery(depute.fullName);
    setCandidates([]);
    setMessage(null);
  };

  const onTopicChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTopic(event.target.value);
  };

  const ask = async (depute: DemoDepute, subject: string) => {
    setStatus("loading");
    setMessage(null);
    setAnswer(null);
    try {
      const params = new URLSearchParams({ depute: depute.uid, sujet: subject });
      const response = await fetch(`/api/demo?${params.toString()}`);
      const payload: DemoAnswer | { error: string } = await response.json();
      if (!response.ok || "error" in payload) {
        setStatus("error");
        setMessage("error" in payload ? payload.error : GENERIC_ERROR);
        return;
      }
      setAnswer(payload);
      setStatus("idle");
    } catch {
      setStatus("error");
      setMessage(GENERIC_ERROR);
    }
  };

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const subject = topic.trim();
    if (subject.length < MIN_QUERY_LENGTH) {
      setMessage("Indiquez un sujet, par exemple un mot du titre d'un texte.");
      return;
    }
    const target = selected ?? (candidates.length === 1 ? (candidates[0] ?? null) : null);
    if (target === null) {
      setMessage("Choisissez un député dans la liste qui s'affiche sous le champ.");
      return;
    }
    choose(target);
    void ask(target, subject);
  };

  const askWith = (depute: DemoDepute | null, subject: string | null) => {
    const nextDepute = depute ?? selected;
    const nextTopic = subject ?? topic.trim();
    if (depute !== null) {
      choose(depute);
    }
    if (subject !== null) {
      setTopic(subject);
    }
    if (nextDepute !== null && nextTopic.length >= MIN_QUERY_LENGTH) {
      void ask(nextDepute, nextTopic);
    }
  };

  return (
    <Section
      id="essayez"
      eyebrow="Essayez"
      title="Comment a voté… ?"
      intro="C'est l'outil le plus utilisé du connecteur. Choisissez un député et un sujet : voici ce que votre IA obtient, avec les mêmes données."
    >
      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <div className="card p-5">
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <div className="relative">
              <label htmlFor="demo-depute" className="mb-1 block text-sm font-semibold">
                Député ou députée
              </label>
              <div className="relative">
                <Search aria-hidden className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
                <input
                  id="demo-depute"
                  type="text"
                  autoComplete="off"
                  value={query}
                  onChange={onQueryChange}
                  placeholder="Tapez un nom de famille"
                  aria-describedby="demo-depute-help"
                  className="card w-full py-2.5 pl-9 pr-3"
                />
              </div>
              <p id="demo-depute-help" className="mt-1 text-xs text-muted">
                Recherche sur le nom et le prénom, sans tenir compte des accents.
              </p>
              {candidates.length > 0 ? (
                <ul aria-label="Députés trouvés" className="card mt-2 max-h-64 divide-y divide-line overflow-auto">
                  {candidates.map((candidate) => {
                    const onPick = () => {
                      choose(candidate);
                    };
                    return (
                      <li key={candidate.uid}>
                        <button
                          type="button"
                          onClick={onPick}
                          className="flex w-full items-baseline justify-between gap-3 px-3 py-2 text-left hover:bg-surface-2"
                        >
                          <span className="font-medium">{candidate.fullName}</span>
                          <span className="text-xs text-muted">{describeDepute(candidate)}</span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </div>

            <div>
              <label htmlFor="demo-sujet" className="mb-1 block text-sm font-semibold">
                Sujet
              </label>
              <input
                id="demo-sujet"
                type="text"
                value={topic}
                onChange={onTopicChange}
                placeholder="Un mot-clé, par exemple « retraites »"
                className="card w-full px-3 py-2.5"
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={status === "loading"}>
              {status === "loading" ? "Recherche…" : "Voir les votes"}
            </button>
            {message !== null ? (
              <p role="alert" className="text-sm text-muted">
                {message}
              </p>
            ) : null}
          </form>

          {deputes.length > 0 || topics.length > 0 ? (
            <div className="mt-6 space-y-4 border-t border-line pt-4">
              {deputes.length > 0 ? (
                <div>
                  <p className="mb-2 text-sm font-semibold">Exemples de députés (sélection du jour, parmi ceux qui ont voté le dernier texte)</p>
                  <ul className="flex flex-wrap gap-2">
                    {deputes.map((depute) => {
                      const onChip = () => {
                        askWith(depute, null);
                      };
                      return (
                        <li key={depute.uid}>
                          <button type="button" onClick={onChip} className="btn px-3 py-1.5 text-sm">
                            {depute.fullName}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null}
              {topics.length > 0 ? (
                <div>
                  <p className="mb-2 text-sm font-semibold">Exemples de sujets (derniers textes votés en entier)</p>
                  <ul className="flex flex-wrap gap-2">
                    {topics.map((example) => {
                      const onChip = () => {
                        askWith(null, example);
                      };
                      return (
                        <li key={example}>
                          <button type="button" onClick={onChip} className="btn px-3 py-1.5 text-left text-sm">
                            {example}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        <div aria-live="polite" className="card min-h-64 overflow-hidden">
          <div className="border-b border-line bg-surface-2 px-5 py-3 font-mono text-xs text-muted">
            {answer
              ? `comment_a_vote(depute="${answer.depute.fullName}", sujet="${answer.topic}")`
              : "Résultat renvoyé à l'IA par comment_a_vote"}
          </div>
          <div className="p-5">
            {answer === null ? (
              <p className="text-muted">
                {status === "loading"
                  ? "Interrogation des données de l'Assemblée…"
                  : "Le résultat s'affichera ici : la position du député sur les scrutins qui correspondent au sujet, avec les liens vers les sources."}
              </p>
            ) : (
              <AnswerView answer={answer} />
            )}
          </div>
        </div>
      </div>
    </Section>
  );
};

const AnswerView: React.FC<{ answer: DemoAnswer }> = ({ answer }) => {
  const { depute, entries, total, topic } = answer;
  return (
    <div>
      <p className="font-semibold">
        {depute.fullName}
        {describeDepute(depute) !== "" ? <span className="font-normal text-muted"> · {describeDepute(depute)}</span> : null}
      </p>
      {entries.length === 0 ? (
        <p className="mt-3 text-muted">Aucun scrutin ne correspond à « {topic} ». Essayez un autre mot-clé.</p>
      ) : (
        <>
          <p className="mt-1 text-sm text-muted">
            {entries.length} premier{entries.length > 1 ? "s" : ""} scrutin{entries.length > 1 ? "s" : ""}
            {total !== null ? ` sur ${total}` : ""} trouvé{entries.length > 1 ? "s" : ""} pour « {topic} ». Un texte donne
            souvent plusieurs scrutins (amendements, articles, ensemble).
          </p>
          <ul className="mt-3 divide-y divide-line">
            {entries.map((entry) => (
              <li key={entry.uid} className="py-3">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <span className="rounded-md border border-line bg-surface-2 px-2 py-0.5 text-sm font-semibold">
                    {entry.position === "unknown" ? "Pas de vote enregistré" : POSITION_LABELS[entry.position]}
                  </span>
                  <ResultBadge result={entry.result} />
                  <span className="text-xs text-muted">{formatDay(entry.date)}</span>
                </div>
                <p className="mt-1 text-sm">{entry.title}</p>
                {entry.dossier !== null ? <p className="text-xs text-muted">{entry.dossier}</p> : null}
                <p className="mt-1 flex flex-wrap gap-x-4 text-xs">
                  <a className="link" href={`/scrutins/${entry.uid}`}>
                    Page du scrutin
                  </a>
                  <a className="link inline-flex items-center gap-1" href={entry.civixUrl} target="_blank" rel="noreferrer">
                    CIVIX <ExternalLink aria-hidden className="size-3" />
                  </a>
                  {entry.assembleeUrl !== null ? (
                    <a className="link inline-flex items-center gap-1" href={entry.assembleeUrl} target="_blank" rel="noreferrer">
                      Assemblée nationale <ExternalLink aria-hidden className="size-3" />
                    </a>
                  ) : null}
                </p>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};
