/**
 * Journal des nouveautés du connecteur, du plus récent au plus ancien.
 *
 * Source unique : la landing l'affiche (section « Nouveautés » et page /nouveautes) et
 * `pnpm changelog` en tire le CHANGELOG.md à la racine du dépôt. À compléter dans chaque PR qui
 * change ce que le connecteur sait faire ; un test vérifie que CHANGELOG.md est à jour.
 */

export type ChangeKind = "nouveau" | "amelioration" | "correction";

export type Change = {
  kind: ChangeKind;
  title: string;
  detail: string;
  /** Numéro de la pull request GitHub qui a apporté le changement. */
  pr: number;
};

export type ChangelogDay = {
  /** Jour de mise en ligne, au format AAAA-MM-JJ. */
  date: string;
  changes: readonly Change[];
};

export const CHANGE_LABELS: Readonly<Record<ChangeKind, string>> = {
  nouveau: "Nouveau",
  amelioration: "Amélioré",
  correction: "Corrigé",
};

export const CHANGELOG: readonly ChangelogDay[] = [
  {
    date: "2026-10-31",
    changes: [
      {
        kind: "correction",
        title: "Un lien exact pour chaque vote cité",
        detail:
          "Les listes de votes donnent maintenant le lien de chaque scrutin vers le site de l'Assemblée nationale. L'assistant n'a plus à deviner une adresse, ce qui menait parfois à une page d'erreur.",
        pr: 57,
      },
    ],
  },
  {
    date: "2026-10-30",
    changes: [
      {
        kind: "nouveau",
        title: "Comparer de 3 à 5 députés",
        detail:
          "Pour chaque paire de députés, la part de scrutins votés de la même façon, avec le nombre de scrutins comparés.",
        pr: 49,
      },
      {
        kind: "amelioration",
        title: "Les groupes analysés de 2012 à aujourd'hui",
        detail:
          "Positions, accords et cohésion des groupes pour chaque législature, de la 14e à la 17e.",
        pr: 47,
      },
      {
        kind: "amelioration",
        title: "La position des groupes dans le suivi d'un sujet",
        detail:
          "Le suivi d'un sujet montre comment chaque groupe a voté sur les derniers votes sur l'ensemble d'un texte.",
        pr: 48,
      },
      {
        kind: "amelioration",
        title: "Une recherche qui accepte le pluriel",
        detail: "« retraites » trouve aussi les scrutins dont le titre dit « retraite ».",
        pr: 50,
      },
      {
        kind: "nouveau",
        title: "Suivre un sujet d'une législature à l'autre",
        detail:
          "Pour un sujet, les scrutins de chaque législature depuis 2012 : nombre, résultats et derniers votes sur l'ensemble d'un texte.",
        pr: 41,
      },
      {
        kind: "nouveau",
        title: "Titres, résultats et votes par groupe de 2012 à 2022",
        detail:
          "Les scrutins des 14e et 15e législatures sont complétés par les archives de l'Assemblée nationale et se cherchent par sujet.",
        pr: 40,
      },
      {
        kind: "nouveau",
        title: "Les votes consultables depuis 2012",
        detail:
          "Les anciens députés et leurs votes sont retrouvés de la 14e à la 16e législature, en plus de la législature en cours.",
        pr: 35,
      },
      {
        kind: "amelioration",
        title: "Des réponses plus rapides",
        detail: "Les réponses déjà obtenues sont partagées entre les serveurs du connecteur.",
        pr: 34,
      },
      {
        kind: "nouveau",
        title: "Les dossiers législatifs dans ChatGPT",
        detail: "La recherche approfondie de ChatGPT trouve et ouvre les dossiers législatifs.",
        pr: 33,
      },
    ],
  },
  {
    date: "2026-10-29",
    changes: [
      {
        kind: "correction",
        title: "Liens vers les scrutins de l'Assemblée",
        detail: "Chaque scrutin renvoie vers la bonne page du site de l'Assemblée nationale.",
        pr: 17,
      },
      {
        kind: "nouveau",
        title: "13 outils d'analyse et d'export",
        detail:
          "Tendances, positions des groupes, bilan d'un député, comparaisons et exports CSV ou JSON, avec la méthode indiquée.",
        pr: 11,
      },
      {
        kind: "correction",
        title: "Audit de sécurité du connecteur",
        detail: "Plafond de requêtes par question, liens contrôlés et citations de tiers signalées.",
        pr: 7,
      },
    ],
  },
];

/** Nombre de changements affichés dans la section de la page d'accueil. */
export const HOME_CHANGES = 5;

/** Les `count` changements les plus récents, regroupés par jour. */
export function latestChanges(count: number, days: readonly ChangelogDay[] = CHANGELOG): ChangelogDay[] {
  const kept: ChangelogDay[] = [];
  let left = count;
  for (const day of days) {
    if (left <= 0) {
      break;
    }
    const changes = day.changes.slice(0, left);
    kept.push({ ...day, changes });
    left -= changes.length;
  }
  return kept;
}
