import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { scrutinListSchema } from "@/lib/civix/schemas";
import { toScrutin } from "@/lib/civix/mappers";

export function fixture(name: string): unknown {
  const path = fileURLToPath(new URL(`./fixtures/${name}.json`, import.meta.url));
  return JSON.parse(readFileSync(path, "utf8"));
}

export function fixtureScrutins(name: string) {
  return scrutinListSchema.parse(fixture(name)).data.attributes.results.map(toScrutin);
}

export const NOW = new Date("2026-10-29T12:00:00+01:00");
