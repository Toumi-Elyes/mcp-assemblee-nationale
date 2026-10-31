"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { GithubLogoIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/cn";
import { GITHUB_URL, SITE_NAME } from "@/lib/config";
import { ThemeSettings } from "./theme-settings";

type NavItem = { href: string; label: string };

const ITEMS: readonly NavItem[] = [
  { href: "/#en-clair", label: "Comment ça marche" },
  { href: "/#demo", label: "Essayer" },
  { href: "/#installer", label: "Installer" },
  { href: "/nouveautes", label: "Nouveautés" },
  { href: "/#faq", label: "Questions" },
];

const PAGE_LABELS: Readonly<Record<string, string>> = {
  "/confidentialite": "Confidentialité",
  "/mentions": "Mentions",
};

function pageLabel(pathname: string): string | null {
  if (pathname.startsWith("/scrutins/")) {
    return "Scrutin";
  }
  return PAGE_LABELS[pathname] ?? null;
}

const linkClass =
  "block whitespace-nowrap border-b-2 border-transparent px-1 py-2 font-display text-base font-semibold text-ink transition-colors hover:text-accent sm:text-lg";

export const SiteNav: React.FC = () => {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const currentPage = pageLabel(pathname);

  return (
    <header className="bg-bg">
      <div className="bg-surface">
        <div className="mx-auto flex w-full max-w-page flex-wrap items-center justify-between gap-x-6 gap-y-1 px-4 py-1 sm:px-6">
          <p className="py-1 text-xs text-ink-soft">
            Projet indépendant et non officiel · données de l'Assemblée nationale via CIVIX
          </p>
          <div className="flex items-center gap-1">
            <ThemeSettings variant="header" />
            <a
              href={GITHUB_URL}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-accent transition-colors hover:text-accent-hover"
            >
              <GithubLogoIcon aria-hidden="true" size={20} weight="bold" />
              <span className="max-sm:sr-only">Code source</span>
            </a>
          </div>
        </div>
      </div>
      <div className="border-b border-line">
        <div className="mx-auto flex w-full max-w-page flex-wrap items-center justify-between gap-x-8 gap-y-2 px-4 py-3 sm:px-6">
          <Link href="/" aria-current={isHome ? "page" : undefined} className="flex flex-col py-1 no-underline">
            <span className="font-display text-2xl font-bold leading-none tracking-tight">{SITE_NAME}</span>
            <span className="text-sm text-ink-soft">Les votes des députés, dans votre assistant IA</span>
          </Link>
          <nav aria-label="Navigation principale" className="w-full lg:w-auto">
            <ul className="-mx-1 flex items-center gap-x-4 overflow-x-auto sm:flex-wrap sm:gap-x-5">
              {ITEMS.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    aria-current={pathname === item.href ? "page" : undefined}
                    className={cn(linkClass, pathname === item.href ? "border-rule" : undefined)}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
              {currentPage !== null ? (
                <li>
                  <span aria-current="page" className={cn(linkClass, "border-rule")}>
                    {currentPage}
                  </span>
                </li>
              ) : null}
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};
