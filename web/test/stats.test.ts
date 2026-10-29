import { describe, expect, it } from "vitest";
import {
  adoptionByKind,
  groupByDossier,
  lastDays,
  latestFinalVotes,
  topDossiers,
  votesPerDay,
  windowCoverage,
} from "@/lib/stats";
import { addDays, dayKey, daysBetween } from "@/lib/stats/dates";
import { groupShares, totalSeats } from "@/lib/stats/groupes";
import { toGroupe } from "@/lib/civix/mappers";
import { groupesSchema } from "@/lib/civix/schemas";
import { fixture, fixtureScrutins, NOW } from "./helpers";

const scrutins = fixtureScrutins("scrutins_page1");

describe("dates", () => {
  it("uses the Paris calendar day", () => {
    expect(dayKey(new Date("2026-10-28T23:30:00Z"))).toBe("2026-10-29");
  });

  it("does day arithmetic across month ends", () => {
    expect(addDays("2026-10-30", 3)).toBe("2026-11-02");
    expect(daysBetween("2026-10-01", "2026-10-29")).toBe(28);
  });
});

describe("windowCoverage", () => {
  it("flags an incomplete window when the oldest fetched vote is too recent", () => {
    const coverage = windowCoverage(scrutins, NOW, 30, false);
    expect(coverage.complete).toBe(false);
    expect(coverage.to).toBe("2026-10-29");
    expect(coverage.from > "2026-09-30").toBe(true);
  });

  it("is complete once the source is exhausted", () => {
    expect(windowCoverage(scrutins, NOW, 30, true)).toEqual({
      from: "2026-09-30",
      to: "2026-10-29",
      complete: true,
    });
  });
});

describe("votesPerDay", () => {
  it("counts every fetched vote inside the covered window", () => {
    const result = votesPerDay(scrutins, NOW, 30);
    const first = result.days[0];
    expect(first?.date).toBe(result.coverage.from);
    expect(result.days.at(-1)?.date).toBe("2026-10-29");
    const inside = scrutins.filter((scrutin) => (scrutin.date ?? "") >= result.coverage.from);
    expect(result.total).toBe(inside.length);
  });

  it("includes days without votes as zero", () => {
    const result = votesPerDay(scrutins, NOW, 7);
    expect(result.days).toHaveLength(7);
    expect(result.days.find((day) => day.date === "2026-10-29")?.count).toBe(0);
  });
});

describe("topDossiers", () => {
  it("orders dossiers by number of votes", () => {
    const { items } = topDossiers(scrutins, NOW, 30, 5);
    expect(items.length).toBeGreaterThan(0);
    for (let index = 1; index < items.length; index += 1) {
      expect(items[index - 1]!.total).toBeGreaterThanOrEqual(items[index]!.total);
    }
    for (const item of items) {
      expect(item.adopted + item.rejected).toBeLessThanOrEqual(item.total);
    }
  });

  it("restricts to the requested window", () => {
    const week = topDossiers(scrutins, NOW, 7, 10).items.reduce((sum, item) => sum + item.total, 0);
    const month = topDossiers(scrutins, NOW, 30, 10).items.reduce((sum, item) => sum + item.total, 0);
    expect(week).toBeLessThanOrEqual(month);
  });
});

describe("adoptionByKind", () => {
  it("sums to the number of votes with a known result", () => {
    const stats = adoptionByKind(scrutins);
    const total = stats.reduce((sum, stat) => sum + stat.total, 0);
    expect(total).toBe(scrutins.filter((scrutin) => scrutin.result !== "inconnu").length);
    for (const stat of stats) {
      expect(stat.adoptionRate).toBeCloseTo(stat.adopted / stat.total);
    }
  });
});

describe("weekly grouping", () => {
  it("keeps only the 7 days ending on the latest vote", () => {
    const week = lastDays(scrutins, 7);
    expect(week.every((scrutin) => scrutin.date >= "2026-10-22")).toBe(true);
    const groups = groupByDossier(week);
    expect(groups.reduce((sum, group) => sum + group.scrutins.length, 0)).toBe(week.length);
  });
});

describe("latestFinalVotes", () => {
  it("only keeps votes on a whole text, newest first", () => {
    const finals = latestFinalVotes(fixtureScrutins("search_scrutins"), 5);
    for (const scrutin of finals) {
      expect(scrutin.isFinalVote).toBe(true);
    }
    const dates = finals.map((scrutin) => scrutin.date ?? "");
    expect([...dates].sort().reverse()).toEqual(dates);
  });

  it("does not treat amendments as final votes", () => {
    const amendments = scrutins.filter((scrutin) => scrutin.type === "amendement");
    expect(amendments.length).toBeGreaterThan(0);
    expect(amendments.some((scrutin) => scrutin.isFinalVote)).toBe(false);
  });
});

describe("groupShares", () => {
  const groupes = groupesSchema.parse(fixture("groupes")).data.attributes.groups.map(toGroupe);

  it("sums the seats", () => {
    expect(totalSeats(groupes)).toBe(577);
  });

  it("returns shares that add up to one, largest group first", () => {
    const shares = groupShares(groupes);
    expect(shares.reduce((sum, item) => sum + item.share, 0)).toBeCloseTo(1);
    expect(shares[0]?.groupe.abbr).toBe("RN");
  });
});

describe("hemicycleSeats", () => {
  it("places one seat per deputy and keeps each group's count", async () => {
    const { hemicycleSeats } = await import("@/lib/stats/hemicycle");
    const sizes = [5, 3, 9, 1];
    const seats = hemicycleSeats(sizes);
    expect(seats).toHaveLength(18);
    sizes.forEach((size, group) => {
      expect(seats.filter((seat) => seat.group === group)).toHaveLength(size);
    });
    expect(hemicycleSeats([])).toEqual([]);
  });
});

describe("buildLiveSnapshot", () => {
  it("serialises the week with counts and keeps the payload JSON safe", async () => {
    const { buildLiveSnapshot } = await import("@/lib/data/live");
    const { liveSnapshotSchema } = await import("@/lib/data/live-schema");
    const week = lastDays(scrutins, 7);
    const groups = groupByDossier(week);
    const counts = new Map([[week[0]!.uid, { pour: 1, contre: 2, abstention: 3, non_votant: 0, total: 6 }]]);
    const snapshot = buildLiveSnapshot({
      generatedAt: NOW,
      counters: { legislature: 17, scrutins: 10, latestDate: "2026-10-28", deputes: 577, groupes: 12 },
      week: { from: "2026-10-22", to: "2026-10-28", total: week.length, groups, counts },
      trends: null,
      groupes: null,
      suggestions: { topics: [], deputes: [] },
      heroChat: null,
    });
    const parsed = liveSnapshotSchema.parse(JSON.parse(JSON.stringify(snapshot)));
    expect(parsed.week?.total).toBe(week.length);
    expect(parsed.week?.groups.length).toBeLessThanOrEqual(6);
    expect(parsed.week?.groups.every((group) => group.scrutins.length <= 3)).toBe(true);
  });
});
