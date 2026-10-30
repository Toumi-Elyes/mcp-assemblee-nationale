import { describe, expect, it } from "vitest";
import { toDay, toPosition, toResult } from "@/lib/civix/mappers";
import {
  deputesSchema,
  scrutinDetailResponseSchema,
  scrutinVotesSchema,
  searchSchema,
  statementsSchema,
} from "@/lib/civix/schemas";
import { cleanTitle, isFinalVoteTitle, matchesName } from "@/lib/text";
import { fixture, fixtureScrutins } from "./helpers";

describe("mappers", () => {
  it("keeps the calendar day of a CIVIX timestamp", () => {
    expect(toDay("2026-10-28T00:00:00+00:00")).toBe("2026-10-28");
    expect(toDay(null)).toBeNull();
  });

  it("maps results and positions", () => {
    expect(toResult("adopté")).toBe("adopte");
    expect(toResult(null, false)).toBe("rejete");
    expect(toResult(undefined)).toBe("inconnu");
    expect(toPosition("pour")).toBe("pour");
    expect(toPosition("???")).toBe("unknown");
  });

  it("builds scrutins with dossier and cleaned title", () => {
    const [first] = fixtureScrutins("scrutins_page1");
    expect(first?.title.endsWith(".")).toBe(false);
    expect(first?.title.charAt(0)).toBe(first?.title.charAt(0).toUpperCase());
    expect(first?.dossier?.label).toBeTruthy();
  });
});

describe("text helpers", () => {
  it("cleans titles", () => {
    expect(cleanTitle("l'amendement n° 1 du projet.")).toBe("L'amendement n° 1 du projet");
  });

  it("detects final votes with both apostrophes", () => {
    expect(isFinalVoteTitle("l'ensemble du projet de loi")).toBe(true);
    expect(isFinalVoteTitle("l’ensemble de la proposition")).toBe(true);
    expect(isFinalVoteTitle("l'amendement n° 3")).toBe(false);
  });

  it("matches names without accents or hyphens", () => {
    expect(matchesName("Audrey Abadie-Amiel", "abadie amiel")).toBe(true);
    expect(matchesName("Mathilde Panot", "Éric")).toBe(false);
  });
});

describe("schemas tolerate real fixtures", () => {
  it("parses votes with counts", () => {
    const parsed = scrutinVotesSchema.parse(fixture("scrutin_votes")).data.attributes;
    expect(parsed.results_global?.total).toBe(90);
    expect(parsed.results_by_group.length).toBeGreaterThan(0);
    expect(parsed.votes.length).toBeGreaterThan(0);
  });

  it("parses a 14th legislature scrutin, which has no group breakdown", () => {
    for (const name of ["scrutin_votes_l14", "scrutin_detail_l14"]) {
      const parsed = scrutinDetailResponseSchema.parse(fixture(name)).data.attributes;
      expect(parsed.results_global?.total).toBe(538);
      expect(parsed.results_by_group).toEqual([]);
    }
    const votes = scrutinVotesSchema.parse(fixture("scrutin_votes_l14")).data.attributes.votes;
    expect(votes.length).toBeGreaterThan(0);
    expect(votes.every((vote) => vote.par_delegation === false)).toBe(true);
  });

  it("parses statements, deputies and search hits", () => {
    expect(statementsSchema.parse(fixture("scrutin_statements")).data.attributes.statements).toHaveLength(1);
    expect(deputesSchema.parse(fixture("deputes")).data.attributes.results.length).toBeGreaterThan(0);
    expect(searchSchema.parse(fixture("search_depute")).results.deputes[0]?.acteur_uid).toBe("PA793214");
  });
});
