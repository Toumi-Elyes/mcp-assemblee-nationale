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
import { ThemeSettings } from "./theme-settings";

type FooterLink = { href: string; label: string };

const PROJECT: readonly FooterLink[] = [
  { href: GITHUB_URL, label: "Code source sur GitHub" },
  { href: GITHUB_ISSUES_URL, label: "Signaler un problème" },
  { href: "/#installer", label: "Installer le connecteur" },
  { href: "/#faq", label: "Questions fréquentes" },
];

const DATA: readonly FooterLink[] = [
  { href: DATA_GOUV_URL, label: "API CIVIX sur data.gouv.fr" },
  { href: CIVIX_SITE, label: "CIVIX" },
  { href: ASSEMBLEE_SITE, label: "Assemblée nationale" },
  { href: LICENCE_URL, label: "Licence Ouverte 2.0" },
];

const LEGAL: readonly FooterLink[] = [
  { href: "/confidentialite", label: "Confidentialité et cookies" },
  { href: "/mentions", label: "Mentions" },
];

const LinkList: React.FC<{ title: string; links: readonly FooterLink[] }> = ({ title, links }) => {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-display text-lg font-semibold">{title}</h2>
      <ul className="flex flex-col gap-2 text-sm">
        {links.map((link) => (
          <li key={link.href}>
            <a href={link.href} className={LINK_TEXT}>
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
    <footer className="border-t-2 border-rule bg-bg py-12">
      <div className="mx-auto flex w-full max-w-page flex-col gap-10 px-4 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col gap-3">
            <p className="font-display text-2xl font-bold leading-none tracking-tight">{SITE_NAME}</p>
            <p className="text-sm text-ink-soft">
              Projet personnel, indépendant et non officiel. Il n'est affilié ni à l'Assemblée nationale ni à CIVIX.
            </p>
          </div>
          <LinkList title="Le projet" links={PROJECT} />
          <LinkList title="Les données" links={DATA} />
          <div className="flex flex-col gap-3">
            <LinkList title="Informations légales" links={LEGAL} />
            <div className="-ml-3">
              <ThemeSettings variant="footer" />
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-3 border-t border-line pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-ink-soft">
            Sauf mention contraire, les données sont publiées sous Licence Ouverte 2.0 (Etalab). Code sous licence MIT.
          </p>
          <a href="#haut" className="inline-flex items-center gap-2 px-3 py-2 text-sm font-bold text-accent transition-colors hover:text-accent-hover">
            <ArrowUpIcon aria-hidden="true" size={20} weight="bold" />
            Haut de page
          </a>
        </div>
      </div>
    </footer>
  );
};
