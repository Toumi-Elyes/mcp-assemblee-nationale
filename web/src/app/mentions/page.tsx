import type { Metadata } from "next";
import { LINK_TEXT } from "@/components/button-styles";
import { LegalPage } from "@/components/legal-page";
import {
  ASSEMBLEE_SITE,
  CIVIX_SITE,
  DATA_GOUV_URL,
  GITHUB_ISSUES_URL,
  GITHUB_URL,
  LICENCE_URL,
} from "@/lib/config";

export const metadata: Metadata = {
  title: "Mentions",
  description: "Projet indépendant, non affilié à l'Assemblée nationale ni à CIVIX. Données sous Licence Ouverte, code sous licence MIT.",
  alternates: { canonical: "/mentions" },
};

const MentionsPage: React.FC = () => {
  return (
    <LegalPage
      title="Mentions"
      intro="Un projet personnel, indépendant et ouvert."
      blocks={[
        {
          title: "Qui édite ce site",
          paragraphs: [
            "Ce site et le connecteur sont un projet personnel d'Elyes Toumi, sans but commercial. Ils ne sont affiliés ni à l'Assemblée nationale ni à CIVIX, et ne sont pas des services officiels.",
          ],
        },
        {
          title: "D'où viennent les données",
          paragraphs: [
            <>
              Les données sont celles de l'
              <a href={ASSEMBLEE_SITE} className={LINK_TEXT}>
                Assemblée nationale
              </a>
              , reprises par l'
              <a href={DATA_GOUV_URL} className={LINK_TEXT}>
                API publique CIVIX
              </a>
              , une initiative indépendante et non officielle (
              <a href={CIVIX_SITE} className={LINK_TEXT}>
                civix.fr
              </a>
              ).
            </>,
            <>
              Elles sont publiées sous{" "}
              <a href={LICENCE_URL} className={LINK_TEXT}>
                Licence Ouverte Etalab 2.0
              </a>
              . Elles sont transmises telles quelles : en cas de doute, vérifiez toujours sur la page du scrutin.
            </>,
          ],
        },
        {
          title: "Code et licence",
          paragraphs: [
            <>
              Le code est disponible sur{" "}
              <a href={GITHUB_URL} className={LINK_TEXT}>
                GitHub
              </a>{" "}
              sous licence MIT, © Elyes Toumi.
            </>,
          ],
        },
        {
          title: "Hébergement",
          paragraphs: ["Le site et le connecteur sont hébergés par Vercel Inc., États-Unis."],
        },
        {
          title: "Contact et signalement",
          paragraphs: [
            <>
              Pour signaler une erreur du site ou du connecteur, ouvrez une demande sur{" "}
              <a href={GITHUB_ISSUES_URL} className={LINK_TEXT}>
                la page des issues GitHub
              </a>
              . Si c'est une donnée qui semble fausse (vote ou député mal enregistré), signalez ce cas plutôt à CIVIX ou à
              l'Assemblée nationale, qui détiennent la donnée d'origine.
            </>,
          ],
        },
      ]}
    />
  );
};

export default MentionsPage;
