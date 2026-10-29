"use client";

import { useState } from "react";
import type { Position } from "@/lib/civix/types";
import { POSITIONS } from "@/lib/civix/types";
import { POSITION_LABELS } from "@/lib/format";
import { normalizeSearch } from "@/lib/text";
import { BUTTON_SECONDARY } from "./button-styles";

export type ExplorerVote = {
  uid: string;
  name: string;
  position: Position;
  byDelegation: boolean;
  groupAbbr: string | null;
};

const PAGE_SIZE = 60;
const ALL = "tous";

const fieldClass = "rounded border border-line bg-raised px-3 py-2 text-base transition hover:bg-hover";

export const VotesExplorer: React.FC<{ votes: readonly ExplorerVote[]; groupOptions: readonly string[] }> = ({
  votes,
  groupOptions,
}) => {
  const [name, setName] = useState("");
  const [position, setPosition] = useState<string>(ALL);
  const [group, setGroup] = useState<string>(ALL);
  const [limit, setLimit] = useState(PAGE_SIZE);

  const wanted = normalizeSearch(name);
  const matches = votes.filter(
    (vote) =>
      (position === ALL || vote.position === position) &&
      (group === ALL || vote.groupAbbr === group) &&
      (wanted === "" || normalizeSearch(vote.name).includes(wanted)),
  );
  const shown = matches.slice(0, limit);

  const onMore = () => {
    setLimit((value) => value + PAGE_SIZE);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="flex flex-col gap-1">
          <label htmlFor="filtre-nom" className="text-sm font-bold">
            Nom
          </label>
          <input
            id="filtre-nom"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setLimit(PAGE_SIZE);
            }}
            placeholder="Chercher un député"
            className={fieldClass}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="filtre-position" className="text-sm font-bold">
            Position
          </label>
          <select
            id="filtre-position"
            value={position}
            onChange={(event) => {
              setPosition(event.target.value);
              setLimit(PAGE_SIZE);
            }}
            className={fieldClass}
          >
            <option value={ALL}>Toutes</option>
            {POSITIONS.map((item) => (
              <option key={item} value={item}>
                {POSITION_LABELS[item]}
              </option>
            ))}
          </select>
        </div>
        {groupOptions.length > 0 ? (
          <div className="flex flex-col gap-1">
            <label htmlFor="filtre-groupe" className="text-sm font-bold">
              Groupe
            </label>
            <select
              id="filtre-groupe"
              value={group}
              onChange={(event) => {
                setGroup(event.target.value);
                setLimit(PAGE_SIZE);
              }}
              className={fieldClass}
            >
              <option value={ALL}>Tous</option>
              {groupOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
        ) : null}
      </div>

      <p className="text-sm text-muted" aria-live="polite">
        {matches.length} députés correspondent{matches.length > shown.length ? `, ${shown.length} affichés` : ""}.
      </p>

      {matches.length === 0 ? (
        <div className="rounded-lg border border-line bg-surface p-6">
          <p className="text-base font-bold">Aucun député ne correspond à ces filtres</p>
          <p className="text-sm text-muted">Modifiez le nom, la position ou le groupe pour élargir la liste.</p>
        </div>
      ) : (
        <ul className="grid gap-2 sm:grid-cols-2">
          {shown.map((vote) => (
            <li key={vote.uid} className="flex items-center justify-between gap-3 rounded bg-surface px-3 py-2 text-sm">
              <span>
                <span className="font-medium">{vote.name}</span>
                {vote.groupAbbr !== null ? <span className="text-muted"> {vote.groupAbbr}</span> : null}
                {vote.byDelegation ? <span className="text-muted"> par délégation</span> : null}
              </span>
              <span className="font-bold">{POSITION_LABELS[vote.position]}</span>
            </li>
          ))}
        </ul>
      )}

      {matches.length > shown.length ? (
        <button type="button" onClick={onMore} className={`${BUTTON_SECONDARY} self-start`}>
          Afficher plus
        </button>
      ) : null}
    </div>
  );
};
