"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { GithubLogoIcon, ListChecksIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/cn";
import { GITHUB_URL, SITE_NAME } from "@/lib/config";

type NavItem = { href: string; label: string };

const ITEMS: readonly NavItem[] = [
  { href: "/#en-direct", label: "Données en direct" },
  { href: "/#demo", label: "Démonstration" },
  { href: "/#installer", label: "Installer" },
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

const linkClass = "block px-3 py-2 text-base font-medium text-ink transition hover:bg-hover";

export const SiteNav: React.FC = () => {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const currentPage = pageLabel(pathname);

  return (
    <header className="bg-bg">
      <p className="bg-surface px-4 py-2 text-center text-xs text-ink-soft sm:px-6">
        Projet indépendant et non officiel · données de l'Assemblée nationale via CIVIX
      </p>
      <div className="border-b border-line">
        <div className="mx-auto flex w-full max-w-page flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
          <Link href="/" className="flex items-center gap-3 py-1">
            <ListChecksIcon aria-hidden="true" size={32} weight="bold" className="text-accent" />
            <span className="flex flex-col">
              <span className="text-lg font-bold leading-6">{SITE_NAME}</span>
              <span className="text-xs text-muted">Les votes des députés, dans votre assistant IA</span>
            </span>
          </Link>
          <a
            href={GITHUB_URL}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-accent transition hover:bg-hover lg:order-last"
          >
            <GithubLogoIcon aria-hidden="true" size={20} weight="bold" />
            Code source
          </a>
          <nav aria-label="Navigation principale" className="w-full lg:w-auto">
            <ul className="flex flex-wrap items-center gap-x-1">
              <li>
                <Link
                  href="/"
                  aria-current={isHome ? "page" : undefined}
                  className={cn(linkClass, isHome ? "text-accent underline underline-offset-8" : undefined)}
                >
                  Accueil
                </Link>
              </li>
              {ITEMS.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className={linkClass}>
                    {item.label}
                  </Link>
                </li>
              ))}
              {currentPage !== null ? (
                <li>
                  <span aria-current="page" className={cn(linkClass, "text-accent underline underline-offset-8")}>
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
