"use client";

import { useState } from "react";
import { POSITIONS, type Position } from "@/lib/civix/types";
import { POSITION_LABELS, formatNumber } from "@/lib/format";
import { fold } from "@/lib/text";

export type ExplorerVote = {
  uid: string;
  name: string;
  position: Position;
  byDelegation: boolean;
  groupAbbr: string | null;
};

const PAGE_SIZE = 100;
const ALL = "all";

type ExplorerProps = { votes: ExplorerVote[]; groupOptions: string[] };

export const VotesExplorer: React.FC<ExplorerProps> = ({ votes, groupOptions }) => {
  const [position, setPosition] = useState<string>(ALL);
  const [group, setGroup] = useState<string>(ALL);
  const [name, setName] = useState("");
  const [limit, setLimit] = useState(PAGE_SIZE);

  const needle = fold(name.trim());
  const filtered = votes.filter(
    (vote) =>
      (position === ALL || vote.position === position) &&
      (group === ALL || vote.groupAbbr === group) &&
      (needle === "" || fold(vote.name).includes(needle)),
  );
  const visible = filtered.slice(0, limit);

  const onPosition = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPosition(event.target.value);
    setLimit(PAGE_SIZE);
  };
  const onGroup = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setGroup(event.target.value);
    setLimit(PAGE_SIZE);
  };
  const onName = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value);
    setLimit(PAGE_SIZE);
  };
  const onMore = () => {
    setLimit((current) => current + PAGE_SIZE);
  };

  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div>
          <label htmlFor="filtre-position" className="mb-1 block text-sm font-semibold">
            Position
          </label>
          <select id="filtre-position" value={position} onChange={onPosition} className="card w-full px-3 py-2">
            <option value={ALL}>Toutes</option>
            {POSITIONS.map((item) => (
              <option key={item} value={item}>
                {POSITION_LABELS[item]}
              </option>
            ))}
          </select>
        </div>
        {groupOptions.length > 0 ? (
          <div>
            <label htmlFor="filtre-groupe" className="mb-1 block text-sm font-semibold">
              Groupe actuel
            </label>
            <select id="filtre-groupe" value={group} onChange={onGroup} className="card w-full px-3 py-2">
              <option value={ALL}>Tous</option>
              {groupOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
        ) : null}
        <div>
          <label htmlFor="filtre-nom" className="mb-1 block text-sm font-semibold">
            Nom
          </label>
          <input
            id="filtre-nom"
            type="search"
            value={name}
            onChange={onName}
            placeholder="Chercher un député"
            className="card w-full px-3 py-2"
          />
        </div>
      </div>
      {groupOptions.length > 0 ? (
        <p className="mt-2 text-xs text-muted">
          Le groupe affiché est le groupe actuel du député, qui peut différer de celui au moment du vote.
        </p>
      ) : null}

      <p role="status" className="mt-4 text-sm text-muted">
        {formatNumber(filtered.length)} vote{filtered.length > 1 ? "s" : ""} sur {formatNumber(votes.length)}.
      </p>
      <ul className="mt-2 grid gap-x-6 sm:grid-cols-2">
        {visible.map((vote) => (
          <li key={vote.uid} className="flex items-baseline justify-between gap-3 border-b border-line py-2 text-sm">
            <span>
              {vote.name}
              {vote.groupAbbr !== null ? <span className="text-muted"> · {vote.groupAbbr}</span> : null}
            </span>
            <span className="whitespace-nowrap font-medium">
              {POSITION_LABELS[vote.position]}
              {vote.byDelegation ? <span className="font-normal text-muted"> (délégation)</span> : null}
            </span>
          </li>
        ))}
      </ul>
      {filtered.length > visible.length ? (
        <button type="button" onClick={onMore} className="btn mt-4">
          Afficher plus ({formatNumber(filtered.length - visible.length)} restants)
        </button>
      ) : null}
    </div>
  );
};
