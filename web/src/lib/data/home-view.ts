import "server-only";
import { cache } from "react";
import {
  adoptionByKind,
  countTargets,
  groupByDossier,
  inWindow,
  lastDays,
  newestDate,
  topDossiers,
  totalSeats,
  votesPerDay,
} from "@/lib/stats";
import { getCounts, getFinalVotes, getGroupes, getPool, getSuggestions } from "./home";
import { getHeroChat } from "./hero-chat";
import { settle } from "./result";
import type { HeroCounters, HomeView, TrendsData, WeekData } from "./view-types";

const WEEK_DAYS = 7;
const TREND_DAYS = 30;
const SCRUTINS_PER_DOSSIER = 3;
const MAX_WEEK_DETAILS = 9;
const TOP_DOSSIERS_SHOWN = 6;

export const getHomeView = cache(async (): Promise<HomeView> => {
  const generatedAt = new Date();
  const [pool, groupes, finals, suggestions, heroChat] = await Promise.all([
    settle(getPool()),
    settle(getGroupes()),
    settle(getFinalVotes()),
    settle(getSuggestions()),
    settle(getHeroChat()),
  ]);

  const weekScrutins = pool.ok ? lastDays(pool.data.scrutins, WEEK_DAYS) : [];
  const weekGroups = groupByDossier(weekScrutins);
  const detailUids = [
    ...countTargets(weekGroups, SCRUTINS_PER_DOSSIER, MAX_WEEK_DETAILS),
    ...(finals.ok ? finals.data.map((scrutin) => scrutin.uid) : []),
  ];
  const counts = await getCounts(detailUids);

  const newest = pool.ok ? newestDate(pool.data.scrutins) : null;
  const oldestWeek = weekScrutins.reduce<string | null>(
    (oldest, scrutin) => (oldest === null || scrutin.date < oldest ? scrutin.date : oldest),
    null,
  );

  const week: WeekData | null =
    pool.ok && newest !== null && oldestWeek !== null
      ? { from: oldestWeek, to: newest, total: weekScrutins.length, groups: weekGroups, counts }
      : null;

  let trends: TrendsData | null = null;
  if (pool.ok) {
    const { scrutins, exhausted } = pool.data;
    const perDay = votesPerDay(scrutins, generatedAt, TREND_DAYS, exhausted);
    const periods = [WEEK_DAYS, TREND_DAYS].map((days) => {
      const { items, coverage } = topDossiers(scrutins, generatedAt, days, TOP_DOSSIERS_SHOWN, exhausted);
      return {
        id: `${days}j`,
        label: `${days} jours`,
        from: coverage.from,
        to: coverage.to,
        complete: coverage.complete,
        items: items.map((item) => ({
          key: item.dossier.key,
          label: item.dossier.label,
          total: item.total,
          adopted: item.adopted,
          rejected: item.rejected,
        })),
      };
    });
    trends = {
      perDay,
      periods,
      kinds: adoptionByKind(inWindow(scrutins, perDay.coverage)),
      kindsCoverage: perDay.coverage,
      finalVotes: finals.ok ? finals.data : null,
      finalCounts: counts,
    };
  }

  const groupList = groupes.ok ? groupes.data : null;
  const counters: HeroCounters = {
    legislature: pool.ok ? pool.data.legislature : null,
    scrutins: pool.ok ? pool.data.legislatureTotal : null,
    latestDate: newest,
    deputes: groupList !== null ? totalSeats(groupList) : null,
    groupes: groupList !== null ? groupList.length : null,
  };

  const suggested = suggestions.ok ? suggestions.data : { topics: [], deputes: [] };
  return {
    generatedAt,
    counters,
    week,
    trends,
    groupes: groupList,
    heroChat: heroChat.ok ? heroChat.data : null,
    suggestions: {
      topics: suggested.topics,
      deputes: suggested.deputes.map((depute) => ({
        uid: depute.uid,
        fullName: depute.fullName,
        groupAbbr: depute.groupAbbr,
        department: depute.department,
      })),
    },
  };
});
