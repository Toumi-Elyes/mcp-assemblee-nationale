export type Capability = {
  tool: string;
  question: string;
  detail: string;
};

export type CapabilityGroup = {
  id: string;
  title: string;
  intro: string;
  items: readonly Capability[];
};

export const CAPABILITY_GROUPS: readonly CapabilityGroup[] = [
  {
    id: "suivre-un-vote",
    title: "Suivre un vote",
    intro: "Retrouver un scrutin, son résultat, les positions de chacun et la suite d'un texte.",
    items: [
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
        tool: "comment_a_vote",
        question: "Comment a voté ma députée sur le budget ?",
        detail: "Donne sa position sur les scrutins d'un sujet, avec le lien de chaque source.",
      },
      {
        tool: "dossier_legislatif",
        question: "Quelles ont été toutes les étapes de vote de la loi de finances 2027 ?",
        detail: "Chronologie des scrutins d'un texte, des articles au vote sur l'ensemble ; les amendements sont comptés.",
      },
      {
        tool: "scrutins_par_periode",
        question: "Quels votes sur l'ensemble d'un texte ont eu lieu le mois dernier ?",
        detail: "Liste les scrutins entre deux dates (90 jours au plus), filtrables par type et par résultat.",
      },
      {
        tool: "votes_serres",
        question: "Quels votes se sont joués à quelques voix seulement ?",
        detail: "Repère les scrutins au résultat serré, par défaut sur l'ensemble d'un texte.",
      },
    ],
  },
  {
    id: "comprendre-une-tendance",
    title: "Comprendre une tendance",
    intro: "Prendre du recul sur l'activité de l'Assemblée, avec la méthode et l'échantillon indiqués.",
    items: [
      {
        tool: "tendances_scrutins",
        question: "Combien de scrutins ces 30 derniers jours, et quelle part a été adoptée ?",
        detail: "Volume de scrutins par semaine, part d'adoption par type de vote et jours les plus chargés.",
      },
      {
        tool: "textes_les_plus_votes",
        question: "Quels textes ont donné lieu au plus de scrutins ces dernières semaines ?",
        detail: "Compte les scrutins par texte. Ce nombre ne mesure pas l'importance du texte.",
      },
      {
        tool: "statistiques_assemblee",
        question: "Combien de scrutins, de députés et de groupes compte la législature en cours ?",
        detail: "Nombre de scrutins, part adoptée (estimée sur un échantillon), effectifs de chaque groupe.",
      },
      {
        tool: "positions_groupes",
        question: "Comment se répartissent les positions des groupes sur les retraites ?",
        detail: "Pour chaque scrutin d'un sujet, la position majoritaire de chaque groupe (ou « partagée »).",
      },
      {
        tool: "accords_entre_groupes",
        question: "Quel est le taux d'accord entre chaque paire de groupes sur le budget ?",
        detail: "Part des scrutins où deux groupes ont pris la même position, sur un échantillon borné.",
      },
      {
        tool: "cohesion_groupes",
        question: "Quelle part des votes de chaque groupe suit sa position majoritaire ?",
        detail: "Mesure l'homogénéité des votes au sein de chaque groupe, sur un sujet ou une période.",
      },
    ],
  },
  {
    id: "un-depute-un-groupe",
    title: "Un député, un groupe",
    intro: "Retrouver une personne ou un groupe, puis regarder ses votes.",
    items: [
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
        tool: "bilan_depute",
        question: "Quel est le bilan des votes de ce député sur les retraites, ces 30 derniers jours ?",
        detail: "Pour, contre, abstentions et absences, et part de votes conformes à la position de son groupe. Décrit, ne classe jamais.",
      },
      {
        tool: "comparer_deputes",
        question: "Sur le budget, quel est le taux de votes identiques entre deux députés ?",
        detail: "Part de scrutins votés de la même façon par deux députés nommés, sur un échantillon borné.",
      },
    ],
  },
  {
    id: "exporter-des-donnees",
    title: "Exporter des données",
    intro: "Récupérer les chiffres dans un fichier, en CSV ou en JSON, pour les ouvrir dans un tableur.",
    items: [
      {
        tool: "exporter_scrutins",
        question: "Je voudrais un fichier CSV des scrutins de septembre sur le logement.",
        detail: "Exporte une liste de scrutins, par dates (90 jours au plus) ou par mots clés.",
      },
      {
        tool: "exporter_votes",
        question: "Je voudrais le vote de chaque député sur ce scrutin, en CSV ou en JSON.",
        detail: "Exporte les votes individuels d'un scrutin.",
      },
    ],
  },
];

export const CHATGPT_COMPATIBILITY: readonly Capability[] = [
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

export const TOOL_COUNT =
  CAPABILITY_GROUPS.reduce((sum, group) => sum + group.items.length, 0) + CHATGPT_COMPATIBILITY.length;

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
  {
    name: "tendances_du_mois",
    label: "Tendances du mois",
    example: "Faire le point sur les 30 derniers jours",
    detail: "Volume de scrutins, part d'adoption par type de vote et textes les plus votés, avec la méthode.",
  },
  {
    name: "bilan_groupe",
    label: "Bilan d'un groupe",
    example: "Dresser le bilan d'un groupe à partir de son sigle",
    detail: "Effectif, homogénéité des votes et convergences avec les autres groupes sur 30 jours.",
  },
  {
    name: "comparer_deux_deputes",
    label: "Comparer deux députés",
    example: "Comparer deux députés sur un sujet de votre choix",
    detail: "Taux de positions identiques, nombre de scrutins comparés et limites de l'échantillon.",
  },
];
