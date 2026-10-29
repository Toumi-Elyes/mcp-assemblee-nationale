import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { scrutinVotesSchema } from "@/lib/civix/schemas";
import { assembleeScrutinUrl } from "@/lib/civix/urls";
import { fixture } from "./helpers";

const BROKEN_SOURCE = "https://www.assemblee-nationale.fr/dyn/17/scrutins/jo7324";

function votesWithBrokenSource() {
  const raw = fixture("scrutin_votes") as { source: { source_urls: string[] } };
  return scrutinVotesSchema.parse({ ...raw, source: { ...raw.source, source_urls: [BROKEN_SOURCE] } });
}

vi.mock("server-only", () => ({}));
vi.mock("@/lib/civix/api", () => ({
  getScrutinVotes: vi.fn(async () => votesWithBrokenSource()),
  getStatements: vi.fn(async () => []),
  listGroupes: vi.fn(async () => []),
  listDeputesPage: vi.fn(async () => ({ deputes: [], total: 0 })),
  listScrutins: vi.fn(async () => ({ scrutins: [], total: 0, hasNext: false })),
}));

describe("assembleeScrutinUrl", () => {
  it("builds the scrutin page from legislature and number", () => {
    expect(assembleeScrutinUrl({ uid: "VTANR5L17V9231", legislature: 17, numero: 9231 })).toBe(
      "https://www.assemblee-nationale.fr/dyn/17/scrutins/9231",
    );
  });

  it("reads the legislature from the uid when it is missing", () => {
    expect(assembleeScrutinUrl({ uid: "VTANR5L16V42", legislature: null, numero: 42 })).toBe(
      "https://www.assemblee-nationale.fr/dyn/16/scrutins/42",
    );
  });

  it("returns null without a usable number, so only the CIVIX link is shown", () => {
    expect(assembleeScrutinUrl({ uid: "VTANR5L17V9231", legislature: 17, numero: null })).toBeNull();
    expect(assembleeScrutinUrl({ uid: "VTANR5L17V9231", legislature: 17, numero: -3 })).toBeNull();
    expect(assembleeScrutinUrl({ uid: "inconnu", legislature: null, numero: 12 })).toBeNull();
  });

  it("ignores the CIVIX source_urls for scrutins", () => {
    const { scrutin } = votesWithBrokenSource().data.attributes;
    expect(assembleeScrutinUrl(scrutin)).toBe("https://www.assemblee-nationale.fr/dyn/17/scrutins/7324");
  });
});

describe("scrutin page links", () => {
  it("never renders an Assemblée link in the broken /scrutins/jo format", async () => {
    const { default: ScrutinPage } = await import("@/app/scrutins/[uid]/page");
    const element = await ScrutinPage({ params: Promise.resolve({ uid: "VTANR5L17V7324" }) });
    const html = renderToStaticMarkup(element);
    expect(html).toContain("https://www.assemblee-nationale.fr/dyn/17/scrutins/7324");
    expect(html).not.toContain("/scrutins/jo");
  });
});
