import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { SITE_URL } from "@/lib/config";
import "./globals.css";

const TITLE = "MCP Assemblée nationale : demandez à votre IA comment votent vos députés";
const DESCRIPTION =
  "Branchez Claude, ChatGPT ou Gemini sur les données publiques de l'Assemblée nationale. Votes, députés, groupes : réponses sourcées, sans interprétation. Gratuit, sans compte.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: "%s | MCP Assemblée nationale" },
  description: DESCRIPTION,
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    type: "website",
    locale: "fr_FR",
    siteName: "MCP Assemblée nationale",
  },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
  alternates: { canonical: "/" },
};

export const viewport: Viewport = {
  colorScheme: "light dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fbfaf7" },
    { media: "(prefers-color-scheme: dark)", color: "#0e131a" },
  ],
};

const RootLayout = ({ children }: { children: ReactNode }) => {
  return (
    <html lang="fr">
      <body className="min-h-screen">
        <a
          href="#contenu"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-accent focus:px-3 focus:py-2 focus:text-accent-ink"
        >
          Aller au contenu
        </a>
        {children}
      </body>
    </html>
  );
};

export default RootLayout;
