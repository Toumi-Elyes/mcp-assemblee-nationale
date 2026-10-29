"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { BankIcon, GithubLogoIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/cn";
import { CTA_LABEL, GITHUB_URL, INSTALL_HREF, SITE_NAME } from "@/lib/config";
import { BUTTON_PRIMARY_SMALL } from "./button-styles";

type NavItem = { id: string; label: string };

const SECTIONS: readonly NavItem[] = [
  { id: "pourquoi", label: "Pourquoi" },
  { id: "fonctionnement", label: "Comment ça marche" },
  { id: "en-direct", label: "En direct" },
  { id: "demo", label: "Démo" },
  { id: "installer", label: "Installer" },
  { id: "faq", label: "Questions" },
];

const PAGE_LABELS: Readonly<Record<string, string>> = {
  "/confidentialite": "Confidentialité",
  "/mentions": "Mentions",
};

const SCROLL_SPY_MARGIN = "-35% 0px -60% 0px";
const STAGGER_MS = 60;
const STAGGER_CAP_MS = 400;

function pageLabel(pathname: string): string | null {
  if (pathname.startsWith("/scrutins/")) {
    return "Scrutin";
  }
  return PAGE_LABELS[pathname] ?? null;
}

const linkBase = "rounded-lg px-3 py-2 text-sm font-medium transition hover:bg-hover";

export const SiteNav: React.FC = () => {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string | null>(null);
  const currentPage = pageLabel(pathname);

  useEffect(() => {
    if (!isHome) {
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActive(entry.target.id);
          }
        }
      },
      { rootMargin: SCROLL_SPY_MARGIN },
    );
    for (const item of SECTIONS) {
      const element = document.getElementById(item.id);
      if (element !== null) {
        observer.observe(element);
      }
    }
    return () => {
      observer.disconnect();
    };
  }, [isHome]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    document.documentElement.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.documentElement.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const onToggle = () => {
    setOpen((value) => !value);
  };
  const onClose = () => {
    setOpen(false);
  };
  const hrefFor = (id: string) => (isHome ? `#${id}` : `/#${id}`);

  return (
    <header className="fixed inset-x-0 top-3 z-50 flex justify-center px-4">
      <nav
        aria-label="Navigation principale"
        className="flex w-full max-w-page items-center justify-between gap-4 rounded-2xl border border-line bg-bg/70 p-2 backdrop-blur-md lg:w-auto lg:max-w-none"
      >
        <Link
          href="/"
          aria-current={isHome && active === null ? "page" : undefined}
          className="flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-semibold transition hover:bg-hover"
        >
          <BankIcon aria-hidden="true" size={20} weight="bold" />
          {SITE_NAME}
        </Link>

        <ul className="hidden items-center gap-1 lg:flex">
          {isHome
            ? SECTIONS.map((item) => (
                <li key={item.id}>
                  <a
                    href={hrefFor(item.id)}
                    aria-current={active === item.id ? "location" : undefined}
                    className={cn(linkBase, active === item.id ? "bg-hover text-ink" : "text-muted hover:text-ink")}
                  >
                    {item.label}
                  </a>
                </li>
              ))
            : null}
          {!isHome ? (
            <>
              <li>
                <Link href="/" className={cn(linkBase, "text-muted hover:text-ink")}>
                  Accueil
                </Link>
              </li>
              {currentPage !== null ? (
                <li>
                  <span aria-current="page" className={cn(linkBase, "block bg-hover text-ink")}>
                    {currentPage}
                  </span>
                </li>
              ) : null}
            </>
          ) : null}
        </ul>

        <div className="flex items-center gap-1">
          <a
            href={GITHUB_URL}
            aria-label="Code source sur GitHub"
            className="hidden rounded-lg p-2 text-muted transition hover:bg-hover hover:text-ink sm:block"
          >
            <GithubLogoIcon aria-hidden="true" size={20} weight="bold" />
          </a>
          <a href={isHome ? INSTALL_HREF : `/${INSTALL_HREF}`} className={cn(BUTTON_PRIMARY_SMALL, "hidden whitespace-nowrap lg:inline-flex")}>
            {CTA_LABEL}
          </a>
          <button
            type="button"
            aria-expanded={open}
            aria-controls="menu-mobile"
            aria-label={open ? "Fermer le menu" : "Ouvrir le menu"}
            onClick={onToggle}
            className="relative size-10 rounded-lg transition hover:bg-hover lg:hidden"
          >
            <span
              className={cn(
                "absolute left-3 top-1/2 h-0.5 w-4 bg-ink transition duration-500",
                open ? "translate-y-0 rotate-45" : "-translate-y-1",
              )}
            />
            <span
              className={cn(
                "absolute left-3 top-1/2 h-0.5 w-4 bg-ink transition duration-500",
                open ? "translate-y-0 -rotate-45" : "translate-y-1",
              )}
            />
          </button>
        </div>
      </nav>

      <div
        id="menu-mobile"
        inert={!open}
        className={cn(
          "fixed inset-0 -z-10 flex flex-col gap-3 bg-bg/95 px-6 pb-12 pt-24 backdrop-blur-2xl transition duration-500 lg:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
      >
        {(isHome ? SECTIONS : [{ id: "", label: "Accueil" }]).map((item, index) => (
          <a
            key={item.label}
            href={item.id === "" ? "/" : hrefFor(item.id)}
            onClick={onClose}
            aria-current={active === item.id && item.id !== "" ? "location" : undefined}
            style={{ transitionDelay: open ? `${Math.min(index * STAGGER_MS, STAGGER_CAP_MS)}ms` : "0ms" }}
            className={cn(
              "text-3xl font-semibold transition duration-500 motion-reduce:translate-y-0",
              open ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0",
              active === item.id && item.id !== "" ? "text-accent" : "text-ink",
            )}
          >
            {item.label}
          </a>
        ))}
        {currentPage !== null ? (
          <span aria-current="page" className="text-3xl font-semibold text-accent">
            {currentPage}
          </span>
        ) : null}
        <a href={GITHUB_URL} onClick={onClose} className="mt-auto text-lg text-muted underline underline-offset-4">
          Code source sur GitHub
        </a>
      </div>
    </header>
  );
};
