import type { Counts, Depute, Groupe, Position, Scrutin, VoteResult } from "@/lib/civix/types";
import type { Coverage, DossierGroup, KindStat, VotesPerDay } from "@/lib/stats";

export type HeroCounters = {
  legislature: number | null;
  scrutins: number | null;
  latestDate: string | null;
  deputes: number | null;
  groupes: number | null;
};

export type DemoDepute = {
  uid: string;
  fullName: string;
  groupAbbr: string | null;
  department: string | null;
};

export type WeekData = {
  from: string;
  to: string;
  total: number;
  groups: DossierGroup[];
  counts: Map<string, Counts>;
};

export type TopDossierItem = {
  key: string;
  label: string;
  total: number;
  adopted: number;
  rejected: number;
};

export type TopDossierPeriod = {
  id: string;
  label: string;
  from: string;
  to: string;
  complete: boolean;
  items: TopDossierItem[];
};

export type TrendsData = {
  perDay: VotesPerDay;
  periods: TopDossierPeriod[];
  kinds: KindStat[];
  kindsCoverage: Coverage;
  finalVotes: Scrutin[] | null;
  finalCounts: Map<string, Counts>;
};

export type HeroChat = {
  question: string;
  depute: Depute;
  position: Position;
  result: VoteResult;
  date: string | null;
  scrutinTitle: string;
  scrutinUid: string;
  counts: Counts | null;
  civixUrl: string;
  assembleeUrl: string | null;
};

export type HomeView = {
  generatedAt: Date;
  counters: HeroCounters;
  week: WeekData | null;
  trends: TrendsData | null;
  groupes: Groupe[] | null;
  suggestions: { topics: string[]; deputes: DemoDepute[] };
  heroChat: HeroChat | null;
};
