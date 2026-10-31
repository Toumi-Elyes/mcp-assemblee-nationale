import { DATA_GOUV_URL } from "@/lib/config";

export type FaqItem = { question: string; answer: string };

export type GlossaryItem = { term: string; definition: string };

export const EN_CLAIR: readonly FaqItem[] = [
  {
    question: "C'est quoi, concrètement ?",
    answer:
      "Un petit module gratuit que l'on ajoute à son assistant IA, comme ChatGPT ou Claude. On l'appelle un connecteur. Il donne à l'assistant l'accès aux votes de l'Assemblée nationale : au lieu de répondre de mémoire, au risque de se tromper, il va chercher le vrai vote.",
  },
  {
    question: "À quoi ça sert ?",
    answer:
      "À savoir qui a voté quoi. Comment a voté votre député sur un texte, ce que l'Assemblée a décidé sur un sujet, quels groupes ont voté pour ou contre. Chaque réponse donne le lien vers la page officielle du vote, pour vérifier vous même.",
  },
  {
    question: "Combien ça coûte ?",
    answer:
      "Rien. Pas d'inscription, pas de carte bancaire, pas de mot de passe. Seul votre abonnement à l'assistant peut être payant : ChatGPT demande une formule payante pour ajouter un connecteur, alors que Claude le permet gratuitement.",
  },
  {
    question: "Il faut s'y connaître en informatique ?",
    answer:
      "Non. Vous copiez une adresse, vous la collez une seule fois dans les réglages de votre assistant, et c'est tout. Comptez deux minutes. Ensuite, vous posez vos questions en français, comme à n'importe qui.",
  },
  {
    question: "Ça marche avec quel assistant ?",
    answer:
      "Avec Claude, même en version gratuite. Avec ChatGPT, en formule payante et depuis le site chatgpt.com. L'application Gemini ne permet pas encore d'ajouter un connecteur, à notre connaissance.",
  },
];

export const GLOSSARY: readonly GlossaryItem[] = [
  { term: "Scrutin", definition: "Un vote à l'Assemblée. Un même texte de loi est souvent voté plusieurs fois : article par article, puis en entier." },
  { term: "Législature", definition: "La période entre deux élections législatives, cinq ans au plus. L'actuelle, la 17e, a commencé en 2024." },
  { term: "Groupe", definition: "Les députés se regroupent par affinité politique, par exemple tous ceux d'un même parti." },
  { term: "Connecteur", definition: "Un module qui permet à votre assistant IA d'aller chercher des informations ailleurs. Son nom technique est MCP." },
  { term: "CIVIX", definition: "Un site gratuit, référencé sur data.gouv.fr, qui republie les données de l'Assemblée nationale. C'est là que le connecteur lit les votes." },
];

export const FAQ: readonly FaqItem[] = [


  {
    question: "Les réponses sont fiables et neutres ?",
    answer:
      "Les chiffres viennent de l'Assemblée nationale et sont transmis tels quels, sans note, sans classement et sans commentaire politique. C'est votre assistant qui rédige la phrase finale : ouvrez le lien de la source pour vérifier le vote.",
  },
  {
    question: "Que deviennent mes données ?",
    answer:
      "Le connecteur reçoit seulement la recherche envoyée par votre assistant, par exemple un nom de député ou un sujet, jamais votre conversation. Il n'y a ni compte, ni cookie, ni historique conservé. Votre assistant applique de son côté sa propre politique de confidentialité.",
  },
  {
    question: "L'assistant peut quand même se tromper ?",
    answer:
      "Oui, il peut mal résumer une réponse, comme avec n'importe quel texte. Les chiffres, eux, viennent de l'Assemblée. C'est pourquoi chaque réponse donne le lien du vote : vérifiez toujours, car un même texte est souvent voté plusieurs fois (modifications, articles, texte entier).",
  },
  {
    question: "D'où viennent les chiffres ?",
    answer: `De l'Assemblée nationale, qui publie ses votes en accès libre. Le connecteur les lit sur CIVIX, un site gratuit référencé sur data.gouv.fr (${DATA_GOUV_URL}), sous Licence Ouverte Etalab 2.0. Un vote très récent peut mettre un peu de temps à apparaître, selon la publication des données.`,
  },
  {
    question: "Ce projet est officiel ?",
    answer:
      "Non. C'est un projet personnel et indépendant, sans lien avec l'Assemblée nationale ni avec CIVIX. Le code est ouvert, sous licence MIT, et chacun peut le lire.",
  },
  {
    question: "Jusqu'où remontent les votes ?",
    answer:
      "Jusqu'au 3 juillet 2012. Les votes de chaque député sont consultables depuis cette date, y compris pour les anciens députés. Pour beaucoup de votes de 2012 à 2014, l'Assemblée n'a publié que les noms des députés qui ont voté autrement que leur groupe : l'assistant le précise quand c'est le cas. Rien n'est disponible avant 2012.",
  },
  {
    question: "Et le Sénat ?",
    answer: "Pas pour l'instant : seule l'Assemblée nationale est couverte.",
  },
];
