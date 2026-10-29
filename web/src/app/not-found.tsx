import Link from "next/link";
import { SiteHeader } from "@/components/site-header";

const NotFound = () => {
  return (
    <>
      <SiteHeader />
      <main id="contenu" className="mx-auto max-w-3xl px-4 py-20 sm:px-6">
        <h1 className="text-3xl font-semibold">Page introuvable</h1>
        <p className="mt-3 text-muted">Ce scrutin ou cette page n&apos;existe pas (ou plus).</p>
        <Link href="/" className="btn btn-primary mt-6">
          Retour à l&apos;accueil
        </Link>
      </main>
    </>
  );
};

export default NotFound;
