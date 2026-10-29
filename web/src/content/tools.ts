export type ToolInfo = {
  name: string;
  params: string;
  does: string;
  example: string;
};

export const TOOLS: readonly ToolInfo[] = [
  {
    name: "rechercher",
    params: "requete, page",
    does: "Cherche à la fois des scrutins, des députés, des groupes et des dossiers.",
    example: "Cherche « aide à mourir » : quels votes et quels dossiers existent ?",
  },
  {
    name: "rechercher_scrutins",
    params: "mots_cles, legislature, page",
    does: "Trouve les votes sur un thème, du plus récent au plus ancien.",
    example: "Quels sont les derniers votes sur l'immigration ?",
  },
  {
    name: "obtenir_scrutin",
    params: "uid",
    does: "Donne le résultat officiel, les pour, contre et abstentions, par groupe.",
    example: "Résume ce scrutin avec le détail par groupe.",
  },
  {
    name: "votes_scrutin",
    params: "uid, groupe, position, nom",
    does: "Liste les votes individuels, filtrables par groupe, position ou nom.",
    example: "Quels députés du groupe Écologiste se sont abstenus sur ce scrutin ?",
  },
  {
    name: "declarations_groupes",
    params: "uid",
    does: "Reprend les explications de vote publiées par les groupes, quand il y en a.",
    example: "Qu'ont déclaré les groupes avant ce vote ?",
  },
  {
    name: "rechercher_deputes",
    params: "nom, groupe, legislature, page",
    does: "Retrouve un député par son nom, sans tenir compte des accents.",
    example: "Trouve-moi les députés qui s'appellent Martin.",
  },
  {
    name: "obtenir_depute",
    params: "uid",
    does: "Affiche la fiche d'un député : groupe, circonscription, liens officiels.",
    example: "Donne-moi la fiche de ce député.",
  },
  {
    name: "comment_a_vote",
    params: "depute, sujet ou scrutin_uid",
    does: "Répond à « comment a voté tel député sur tel sujet » avec les liens sources.",
    example: "Comment a voté Mathilde Panot sur le budget ?",
  },
  {
    name: "lister_groupes",
    params: "aucun",
    does: "Liste les groupes parlementaires avec leur sigle et leur effectif.",
    example: "Liste les groupes et leur nombre de députés.",
  },
  {
    name: "obtenir_groupe",
    params: "abbr",
    does: "Présente un groupe : nom complet, effectif, législature.",
    example: "Présente-moi le groupe LIOT.",
  },
  {
    name: "search",
    params: "query",
    does: "Recherche au format attendu par la recherche approfondie de ChatGPT.",
    example: "Fais une recherche approfondie sur les votes liés au logement.",
  },
  {
    name: "fetch",
    params: "id",
    does: "Récupère un résultat de `search` en entier, au même format.",
    example: "Ouvre le résultat n° 1 et détaille-le.",
  },
];

export type PromptInfo = { name: string; param: string; does: string; example: string };

export const PROMPTS: readonly PromptInfo[] = [
  {
    name: "resumer_scrutin",
    param: "sujet",
    does: "Retrouve le vote le plus pertinent sur un sujet et le résume : date, résultat, décomptes, groupes.",
    example: "Résumer un scrutin sur « retraites ».",
  },
  {
    name: "mon_depute",
    param: "nom",
    does: "Présente un député, puis propose de regarder ses votes sur un sujet de votre choix.",
    example: "Présenter le député « Marine Le Pen ».",
  },
  {
    name: "comparer_groupes",
    param: "sujet",
    does: "Compare la position des groupes sur un sujet, avec leurs déclarations publiques.",
    example: "Comparer les groupes sur « budget 2026 ».",
  },
];
