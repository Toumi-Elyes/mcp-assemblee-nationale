import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { CHANGELOG, latestChanges } from "@/content/changelog";
import { changelogDay, changelogMarkdown } from "@/lib/changelog";

function change(pr: number) {
  return { kind: "nouveau" as const, title: `Changement ${pr}`, detail: "Détail.", pr };
}

const CHANGELOG_PATH = fileURLToPath(new URL("../../CHANGELOG.md", import.meta.url));

describe("changelog", () => {
  it("lists days from newest to oldest, once each, with valid dates", () => {
    const dates = CHANGELOG.map((day) => day.date);
    expect(dates.every((date) => /^\d{4}-\d{2}-\d{2}$/.test(date))).toBe(true);
    expect([...dates].sort().reverse()).toEqual(dates);
    expect(new Set(dates).size).toBe(dates.length);
    expect(CHANGELOG.every((day) => day.changes.length > 0)).toBe(true);
  });

  it("links every change to a distinct pull request", () => {
    const prs = CHANGELOG.flatMap((day) => day.changes.map((change) => change.pr));
    expect(prs.every((pr) => Number.isInteger(pr) && pr > 0)).toBe(true);
    expect(new Set(prs).size).toBe(prs.length);
  });

  it("keeps the copy free of hyphens and of trailing periods in titles", () => {
    for (const change of CHANGELOG.flatMap((day) => day.changes)) {
      expect(change.title).not.toMatch(/-|\.$/);
      expect(change.detail).not.toMatch(/ - /);
    }
  });

  it("keeps only the latest changes for the home page", () => {
    const days = latestChanges(3, [
      { date: "2026-10-30", changes: [change(1), change(2)] },
      { date: "2026-10-29", changes: [change(3), change(4)] },
    ]);
    expect(days.map((day) => day.changes.map((item) => item.pr))).toEqual([[1, 2], [3]]);
    expect(latestChanges(0)).toEqual([]);
  });

  it("formats days in French", () => {
    expect(changelogDay("2026-10-30")).toBe("30 octobre 2026");
  });

  it("keeps CHANGELOG.md in sync (pnpm changelog rewrites it)", () => {
    const expected = changelogMarkdown();
    if (process.env.UPDATE_CHANGELOG === "1") {
      writeFileSync(CHANGELOG_PATH, expected, "utf8");
    }
    expect(readFileSync(CHANGELOG_PATH, "utf8")).toBe(expected);
  });
});
