import { z } from "zod";

const text = z.string().nullish();

export const paginationSchema = z
  .object({
    page: z.number().nullish(),
    page_size: z.number().nullish(),
    next_page: z.number().nullish(),
    count_total: z.number().nullish(),
    count_estimated: z.number().nullish(),
  })
  .nullish();

const metaSchema = z.object({ pagination: paginationSchema }).nullish();

const sourceSchema = z
  .object({
    source_urls: z.array(z.string()).default([]),
    civix_urls: z.record(z.string(), z.string()).default({}),
  })
  .nullish();

const objetSchema = z
  .object({
    libelle: text,
    dossierLegislatif: z.object({ libelle: text, dossierRef: text }).nullish(),
  })
  .nullish();

export const scrutinSummarySchema = z.object({
  uid: z.string(),
  legislature: z.number().nullish(),
  numero: z.number().nullish(),
  date_scrutin: z.string().nullish(),
  titre: z.string().default(""),
  objet: objetSchema,
  sort: z.object({ code: text, libelle: text }).nullish(),
  type: text,
  context: text,
});

export const scrutinListSchema = z.object({
  meta: metaSchema,
  data: z.object({ attributes: z.object({ results: z.array(scrutinSummarySchema).default([]) }) }),
});

const countsShape = {
  pour: z.number().default(0),
  contre: z.number().default(0),
  abstention: z.number().default(0),
  non_votant: z.number().default(0),
  total: z.number().default(0),
};

export const countsSchema = z.object(countsShape);
export const groupCountsSchema = z.object({ groupe_uid: z.string().nullish(), ...countsShape });

// Pour les 14e et 15e législatures, CIVIX ne ventile pas les votes par groupe : il renvoie une seule
// ligne `groupe_uid: null` qui reprend le décompte global. On l'écarte.
const groupBreakdownSchema = z
  .array(groupCountsSchema)
  .default([])
  .transform((rows) => rows.flatMap((row) => (row.groupe_uid ? [{ ...row, groupe_uid: row.groupe_uid }] : [])));

export const voteSchema = z.object({
  deputy_uid: z.string(),
  prenom: z.string().default(""),
  nom: z.string().default(""),
  position: z.string().default("unknown"),
  // `null` pour les 14e et 15e législatures : la délégation n'y est pas précisée.
  par_delegation: z
    .boolean()
    .nullish()
    .transform((value) => value ?? false),
});

const scrutinDetailSchema = z.object({
  uid: z.string(),
  numero: z.number().nullish(),
  legislature: z.number().nullish(),
  date_scrutin: z.string().nullish(),
  titre: z.string().default(""),
  objet: objetSchema,
  sort_code: text,
  sort_libelle: text,
  is_adopted: z.boolean().nullish(),
  official_result: text,
  majority_rule: text,
  vote_mode: text,
  type_vote: z.object({ libelleTypeVote: text }).nullish(),
  demandeur: z.object({ texte: text }).nullish(),
  tags: z.array(z.string()).default([]),
});

export const scrutinVotesSchema = z.object({
  source: sourceSchema,
  data: z.object({
    attributes: z.object({
      scrutin: scrutinDetailSchema,
      results_global: countsSchema.nullish(),
      results_by_group: groupBreakdownSchema,
      votes: z.array(voteSchema).default([]),
    }),
  }),
});

export const scrutinDetailResponseSchema = z.object({
  source: sourceSchema,
  data: z.object({
    attributes: z.object({
      scrutin: scrutinDetailSchema,
      results_global: countsSchema.nullish(),
      results_by_group: groupBreakdownSchema,
    }),
  }),
});

export const statementsSchema = z.object({
  data: z.object({
    attributes: z.object({
      statements: z
        .array(
          z.object({
            groupe_uid: text,
            groupe_abrev: text,
            groupe_libelle: text,
            vote_position: text,
            statement: z.string().default(""),
            status: text,
          }),
        )
        .default([]),
    }),
  }),
});

export const groupeSchema = z.object({
  uid: z.string(),
  abbr: z.string(),
  libelle: z.string().default(""),
  legislature: z.number().nullish(),
  effectif: z.number().nullish(),
  urls: z.object({ page: text }).nullish(),
});

export const groupesSchema = z.object({
  data: z.object({ attributes: z.object({ groups: z.array(groupeSchema).default([]) }) }),
});

export const deputeSchema = z.object({
  uid: z.string(),
  prenom: z.string().default(""),
  nom: z.string().default(""),
  circ_num: z.number().nullish(),
  circ_departement: text,
  groupe_abrev: text,
  groupe_libelle: text,
  urls: z.object({ civix_page: text, assemblee: text }).nullish(),
});

export const deputesSchema = z.object({
  meta: metaSchema,
  data: z.object({ attributes: z.object({ results: z.array(deputeSchema).default([]) }) }),
});

export const deputeDetailSchema = z.object({
  data: z.object({ attributes: z.object({ deputy: deputeSchema }) }),
});

export const searchSchema = z.object({
  results: z
    .object({
      deputes: z
        .array(
          z.object({
            acteur_uid: z.string(),
            prenom: z.string().default(""),
            nom: z.string().default(""),
            groupe_libelle_abrev: text,
            circ_departement: text,
          }),
        )
        .default([]),
    })
    .default({ deputes: [] }),
});

export type ScrutinSummaryDto = z.infer<typeof scrutinSummarySchema>;
export type ScrutinVotesDto = z.infer<typeof scrutinVotesSchema>;
export type ScrutinDetailResponseDto = z.infer<typeof scrutinDetailResponseSchema>;
export type StatementsDto = z.infer<typeof statementsSchema>;
export type GroupeDto = z.infer<typeof groupeSchema>;
export type DeputeDto = z.infer<typeof deputeSchema>;
