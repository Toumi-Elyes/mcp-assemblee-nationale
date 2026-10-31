import type { Metadata } from "next";
import { AudienceChoice } from "@/components/audience-choice";
import { LINK_TEXT } from "@/components/button-styles";
import { LegalPage } from "@/components/legal-page";
import { GITHUB_ISSUES_URL } from "@/lib/config";

export const metadata: Metadata = {
  title: "Confidentialité",
  description: "Ce site n'utilise aucun cookie ; il compte ses visites de façon anonyme. Le connecteur ne reçoit que la recherche envoyée par l'assistant.",
  alternates: { canonical: "/confidentialite" },
};

const ConfidentialitePage: React.FC = () => {
  return (
    <LegalPage
      title="Confidentialité"
      intro="En bref : ce site compte ses visites sans vous identifier, et le connecteur ne lit jamais votre conversation."
      blocks={[
        {
          title: "Ce site",
          paragraphs: [
            "Il n'utilise aucun cookie, aucun traceur publicitaire et aucune publicité. Il ne dépose rien sur votre appareil.",
            "Pour estimer sa fréquentation et dimensionner le connecteur, il compte les visites avec Vercel Web Analytics, l'outil de mesure de son hébergeur. Cette mesure est anonyme et sans cookie : pour chaque page vue, elle note la page (sans ses paramètres), le site d'où vous venez, le pays et la région, le type d'appareil, le système et le navigateur. Une visite est reconnue sur 24 heures au plus par une empreinte calculée à partir de la requête, qui n'est pas conservée plus longtemps. Rien ne permet de vous identifier ni de vous suivre sur d'autres sites, et les chiffres ne sont consultés que sous forme de totaux.",
            "Vous pouvez refuser cette mesure : votre choix est gardé dans le stockage local de votre navigateur (clé « mesure-audience »), et plus rien n'est envoyé. Si votre navigateur envoie le signal « Global Privacy Control », vos visites ne sont jamais mesurées.",
            <AudienceChoice key="choix-mesure" />,
            "Les polices de caractères sont servies par ce site, sans appel à un service tiers.",
            "Si vous choisissez un thème dans « Paramètres d'affichage », ce choix est gardé dans le stockage local de votre navigateur (clé « theme »). Il ne quitte jamais votre appareil et n'est pas un cookie.",
          ],
        },
        {
          title: "La démonstration en direct",
          paragraphs: [
            "Quand vous tapez un nom de député ou un sujet, ce texte est envoyé à ce site dans l'adresse de la requête (par exemple « /api/demo?sujet=budget »), puis transmis à l'API CIVIX pour trouver les résultats. Comme il figure dans l'adresse, il peut apparaître dans les journaux techniques de requêtes de l'hébergeur. Le code du projet ne l'enregistre pas.",
            "Pour que deux personnes qui posent la même question partagent la même réponse, les réponses sont conservées par le réseau de diffusion de l'hébergeur pendant 10 minutes, et peuvent être servies jusqu'à environ une heure ensuite en attendant leur renouvellement. Rien n'est relié à une personne : aucun compte, aucun cookie, aucun traceur.",
          ],
        },
        {
          title: "Le connecteur",
          paragraphs: [
            "Le serveur du connecteur reçoit seulement la recherche envoyée par votre assistant, par exemple un nom de député ou un sujet. Il ne reçoit jamais votre conversation, ne demande aucun compte, n'utilise aucun cookie et ne garde aucun historique de vos questions.",
          ],
        },
        {
          title: "L'hébergeur et votre assistant",
          paragraphs: [
            "L'hébergeur du site et du connecteur peut tenir des journaux techniques d'accès (adresse IP, page demandée, date) pour assurer la sécurité et le bon fonctionnement du service. Le code du projet n'y écrit pas vos questions.",
            "Votre assistant (Claude, ChatGPT, Gemini) applique de son côté sa propre politique de confidentialité à vos conversations.",
          ],
        },
        {
          title: "Une question ?",
          paragraphs: [
            <>
              Ouvrez une demande sur{" "}
              <a href={GITHUB_ISSUES_URL} className={LINK_TEXT}>
                la page des issues GitHub du projet
              </a>
              .
            </>,
          ],
        },
      ]}
    />
  );
};

export default ConfidentialitePage;
