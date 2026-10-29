import { z } from "zod";
import type { LiveSnapshot } from "./view-types";

z.config({ jitless: true });

const counts = z.object({
  pour: z.number(),
  contre: z.number(),
  abstention: z.number(),
  non_votant: z.number(),
  total: z.number(),
});

const scrutin = z.object({
  uid: z.string(),
  date: z.string().nullable(),
  title: z.string(),
  result: z.enum(["adopte", "rejete", "inconnu"]),
  counts: counts.nullable(),
});

const group = z.object({
  key: z.string(),
  label: z.string().nullable(),
  count: z.number(),
  adopted: z.number(),
  rejected: z.number(),
  scrutins: z.array(scrutin),
});

export const liveSnapshotSchema = z.object({
  generatedAt: z.string(),
  counters: z.object({
    legislature: z.number().nullable(),
    scrutins: z.number().nullable(),
    latestDate: z.string().nullable(),
    deputes: z.number().nullable(),
    groupes: z.number().nullable(),
  }),
  week: z
    .object({
      from: z.string(),
      to: z.string(),
      total: z.number(),
      hiddenGroups: z.number(),
      groups: z.array(group),
    })
    .nullable(),
}) satisfies z.ZodType<LiveSnapshot>;
