import type { Metadata, Viewport } from "next";
import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";
import { SiteFooter } from "@/components/site-footer";
import { SiteNav } from "@/components/site-nav";
import { SITE_NAME, SITE_URL } from "@/lib/config";
import "./globals.css";

const TITLE = "Comment ont voté vos députés ? Posez la question à votre assistant IA";
const DESCRIPTION =
  "Connecteur gratuit pour Claude et ChatGPT : les votes des députés de l'Assemblée nationale, chiffres officiels et source de chaque scrutin. Sans compte.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: `%s | ${SITE_NAME}` },
  description: DESCRIPTION,
  applicationName: SITE_NAME,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "fr_FR",
    siteName: SITE_NAME,
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "light dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#131209" },
  ],
};

const RootLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <html lang="fr" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body id="haut" className="min-h-screen font-sans text-base">
        <a
          href="#contenu"
          className="sr-only rounded-lg bg-accent px-3 py-2 text-base font-semibold text-on-accent focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50"
        >
          Aller au contenu
        </a>
        <SiteNav />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
};

export default RootLayout;
