import Link from "next/link";
import { Landmark } from "lucide-react";

const LINKS = [
  { href: "/#semaine", label: "Cette semaine" },
  { href: "/#tendances", label: "Tendances" },
  { href: "/#groupes", label: "Groupes" },
  { href: "/#essayez", label: "Essayez" },
  { href: "/#outils", label: "Outils" },
  { href: "/#installer", label: "Installer" },
];

export const SiteHeader: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-serif text-lg font-semibold">
          <Landmark aria-hidden className="size-5 text-accent" />
          MCP Assemblée nationale
        </Link>
        <nav aria-label="Sections" className="hidden gap-5 text-sm md:flex">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="text-muted hover:text-ink">
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};
