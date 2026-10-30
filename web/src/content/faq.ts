import { DATA_GOUV_URL } from "@/lib/config";

export type FaqItem = { question: string; answer: string };

export const FAQ: readonly FaqItem[] = [
  {
    question: "Que fait ce connecteur, concrètement ?",
    answer:
      "Il permet à votre assistant IA de consulter les scrutins, les députés et les groupes de l'Assemblée nationale pendant la conversation, puis de citer le lien de chaque source. Vous posez votre question normalement, en français.",
  },
  {
    question: "Combien ça coûte ?",
    answer:
      "Rien. Le connecteur, l'accès aux données et l'hébergement sont gratuits, sans compte ni clé. Seul l'abonnement à votre assistant peut être payant : ChatGPT demande un plan payant pour ajouter un connecteur personnalisé, alors que Claude en autorise un sur son plan gratuit.",
  },
  {
    question: "C'est trop technique pour moi ?",
    answer:
      "Non. Il suffit de copier une adresse et de la coller dans les réglages de votre assistant. Les étapes sont détaillées plus haut pour chaque assistant, avec un bouton qui copie l'adresse.",
  },
  {
    question: "Les réponses sont fiables et neutres ?",
    answer:
      "Les chiffres viennent des données ouvertes de l'Assemblée nationale et sont transmis tels quels, sans note, sans classement et sans commentaire politique. C'est votre assistant qui rédige la phrase finale : ouvrez le lien de la source pour vérifier le scrutin.",
  },
  {
    question: "Que deviennent mes données ?",
    answer:
      "Le serveur reçoit seulement la recherche envoyée par votre assistant, par exemple un nom de député ou un sujet, jamais votre conversation. Il n'y a ni compte, ni cookie, ni historique conservé. Votre assistant applique de son côté sa propre politique de confidentialité.",
  },
  {
    question: "Ça marche avec mon assistant ?",
    answer:
      "Avec Claude, y compris sur le plan gratuit. Avec ChatGPT, sur les plans payants et depuis le navigateur. L'application grand public de Gemini ne permet pas d'ajouter un connecteur personnalisé, à notre connaissance ; Gemini CLI, en revanche, fonctionne avec la même adresse.",
  },
  {
    question: "L'assistant peut quand même se tromper ?",
    answer:
      "Oui, il peut mal résumer une réponse, comme avec n'importe quel texte. Les chiffres, eux, viennent du serveur. C'est pourquoi chaque réponse cite la page du scrutin : vérifiez toujours le vote cité, car un même texte donne souvent plusieurs scrutins (amendements, articles, ensemble).",
  },
  {
    question: "D'où viennent les chiffres ?",
    answer: `De l'Assemblée nationale, reprise par l'API publique CIVIX référencée sur data.gouv.fr (${DATA_GOUV_URL}). Les données sont sous Licence Ouverte Etalab 2.0. Un vote très récent peut mettre un peu de temps à apparaître, selon la publication des données.`,
  },
  {
    question: "Ce projet est officiel ?",
    answer:
      "Non. C'est un projet personnel et indépendant, sans lien avec l'Assemblée nationale ni avec CIVIX. Le code est ouvert, sous licence MIT, et chacun peut le lire.",
  },
  {
    question: "Jusqu'où remontent les votes ?",
    answer:
      "Jusqu'au premier scrutin de la 14e législature, le 3 juillet 2012. Les votes de chaque député sont consultables de la 14e à la 17e législature, y compris pour les anciens députés. Pour les 14e et 15e législatures (2012 à 2022), la source ne donne ni le titre ni le décompte par groupe des scrutins : l'assistant les retrouve par date ou par numéro, pas par sujet. Rien n'est disponible avant 2012.",
  },
  {
    question: "Et le Sénat ?",
    answer: "Pas pour l'instant : seule l'Assemblée nationale est couverte.",
  },
];
