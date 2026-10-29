export type Capability = {
  tool: string;
  question: string;
  detail: string;
};

export const CAPABILITIES: readonly Capability[] = [
  {
    tool: "rechercher",
    question: "Quels votes et quels dossiers existent sur l'aide à mourir ?",
    detail: "Cherche d'un coup dans les scrutins, les députés, les groupes et les dossiers.",
  },
  {
    tool: "rechercher_scrutins",
    question: "Quels sont les derniers votes sur l'immigration ?",
    detail: "Retrouve les votes d'un thème, du plus récent au plus ancien, avec leur date et leur résultat.",
  },
  {
    tool: "obtenir_scrutin",
    question: "Quel a été le résultat de ce vote, groupe par groupe ?",
    detail: "Donne adopté ou rejeté, les pour, les contre, les abstentions et le détail par groupe.",
  },
  {
    tool: "votes_scrutin",
    question: "Quels députés d'un groupe donné se sont abstenus sur ce scrutin ?",
    detail: "Liste les votes individuels, filtrables par groupe, par position ou par nom.",
  },
  {
    tool: "declarations_groupes",
    question: "Qu'ont expliqué les groupes avant ce vote ?",
    detail: "Reprend les explications de vote publiées par les groupes, quand il y en a.",
  },
  {
    tool: "rechercher_deputes",
    question: "Quels députés s'appellent Martin ?",
    detail: "Retrouve un député par son nom, sans tenir compte des accents ni de la casse.",
  },
  {
    tool: "obtenir_depute",
    question: "Dans quel groupe siège ce député, et dans quelle circonscription ?",
    detail: "Affiche la fiche d'un député avec ses liens officiels.",
  },
  {
    tool: "comment_a_vote",
    question: "Comment a voté ma députée sur le budget ?",
    detail: "Donne sa position sur les scrutins d'un sujet, avec le lien de chaque source.",
  },
  {
    tool: "lister_groupes",
    question: "Combien de députés compte chaque groupe de l'Assemblée ?",
    detail: "Liste les groupes avec leur sigle, leur nom complet et leur effectif.",
  },
  {
    tool: "obtenir_groupe",
    question: "Quel est le nom complet de ce groupe, et quel est son effectif ?",
    detail: "Présente un groupe à partir de son sigle.",
  },
  {
    tool: "search",
    question: "Recherche approfondie : quels votes concernent le logement ?",
    detail: "Même recherche, au format attendu par la recherche approfondie de ChatGPT.",
  },
  {
    tool: "fetch",
    question: "Quel est le détail complet du premier résultat ?",
    detail: "Ouvre en entier un résultat de la recherche approfondie.",
  },
];

export type ReadyPrompt = { name: string; label: string; example: string; detail: string };

export const READY_PROMPTS: readonly ReadyPrompt[] = [
  {
    name: "resumer_scrutin",
    label: "Résumer un scrutin",
    example: "Résumer le scrutin sur « retraites »",
    detail: "Retrouve le vote le plus pertinent, puis donne la date, le résultat, les décomptes et les groupes.",
  },
  {
    name: "mon_depute",
    label: "Mon député",
    example: "Présenter le député « Marie Dupont »",
    detail: "Présente un député, puis propose de regarder ses votes sur le sujet de votre choix.",
  },
  {
    name: "comparer_groupes",
    label: "Comparer les groupes",
    example: "Comparer les groupes sur « budget 2026 »",
    detail: "Met côte à côte la position des groupes sur un sujet, avec leurs déclarations publiques.",
  },
];
