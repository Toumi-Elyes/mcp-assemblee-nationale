export type VoteResult = "adopte" | "rejete" | "inconnu";

export type Position = "pour" | "contre" | "abstention" | "non_votant" | "unknown";

export type Dossier = { key: string; label: string };

export type Scrutin = {
  uid: string;
  legislature: number | null;
  numero: number | null;
  date: string | null;
  title: string;
  dossier: Dossier | null;
  result: VoteResult;
  type: string | null;
  isFinalVote: boolean;
};

export type Counts = {
  pour: number;
  contre: number;
  abstention: number;
  non_votant: number;
  total: number;
};

export type Groupe = {
  uid: string;
  abbr: string;
  label: string;
  size: number;
  legislature: number | null;
  url: string | null;
};

export type Depute = {
  uid: string;
  firstName: string;
  lastName: string;
  fullName: string;
  groupAbbr: string | null;
  groupLabel: string | null;
  department: string | null;
  civixUrl: string;
  assembleeUrl: string;
};

export const POSITIONS: readonly Position[] = ["pour", "contre", "abstention", "non_votant"];
