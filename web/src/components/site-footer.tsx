import { ArrowUpIcon } from "@phosphor-icons/react/dist/ssr";
import {
  ASSEMBLEE_SITE,
  CIVIX_SITE,
  DATA_GOUV_URL,
  GITHUB_ISSUES_URL,
  GITHUB_URL,
  LICENCE_URL,
  SITE_NAME,
} from "@/lib/config";
import { LINK_TEXT } from "./button-styles";

type FooterLink = { href: string; label: string };

const PROJECT: readonly FooterLink[] = [
  { href: GITHUB_URL, label: "Code source sur GitHub" },
  { href: GITHUB_ISSUES_URL, label: "Signaler un problème" },
  { href: "/confidentialite", label: "Confidentialité" },
  { href: "/mentions", label: "Mentions" },
];

const DATA: readonly FooterLink[] = [
  { href: DATA_GOUV_URL, label: "API CIVIX sur data.gouv.fr" },
  { href: CIVIX_SITE, label: "CIVIX" },
  { href: ASSEMBLEE_SITE, label: "Assemblée nationale" },
  { href: LICENCE_URL, label: "Licence Ouverte Etalab 2.0" },
];

const LinkList: React.FC<{ title: string; links: readonly FooterLink[] }> = ({ title, links }) => {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold">{title}</h2>
      <ul className="flex flex-col gap-2 text-sm text-muted">
        {links.map((link) => (
          <li key={link.href}>
            <a href={link.href} className={`${LINK_TEXT} hover:text-ink`}>
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export const SiteFooter: React.FC = () => {
  return (
    <footer className="bg-surface py-16">
      <div className="mx-auto flex w-full max-w-page flex-col gap-10 px-4 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-3">
          <div className="flex flex-col gap-3">
            <p className="text-base font-semibold">{SITE_NAME}</p>
            <p className="max-w-hero text-sm text-muted">
              Projet personnel et indépendant, sans lien avec l'Assemblée nationale ni avec CIVIX. Code sous licence
              MIT, données sous Licence Ouverte Etalab 2.0.
            </p>
          </div>
          <LinkList title="Le projet" links={PROJECT} />
          <LinkList title="Les données" links={DATA} />
        </div>
        <a
          href="#haut"
          className="inline-flex items-center gap-2 self-start rounded-lg px-3 py-2 text-sm font-semibold transition hover:bg-hover"
        >
          <ArrowUpIcon aria-hidden="true" size={20} weight="bold" />
          Retour en haut
        </a>
      </div>
    </footer>
  );
};
