import Link from "next/link";
import { ArrowLeftIcon } from "@phosphor-icons/react/dist/ssr";
import { BUTTON_PRIMARY } from "@/components/button-styles";

const NotFound: React.FC = () => {
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col items-start gap-6 px-4 pb-24 pt-12 sm:px-6">
      <p className="tabular text-6xl font-bold text-muted">404</p>
      <h1 className="font-serif max-w-hero text-4xl font-bold">Cette page n'existe pas</h1>
      <p className="max-w-hero text-lg text-muted">
        L'adresse contient une erreur, ou le scrutin n'existe pas dans les données de l'Assemblée nationale.
      </p>
      <Link href="/" className={BUTTON_PRIMARY}>
        <ArrowLeftIcon aria-hidden="true" size={20} weight="bold" />
        Retour à l'accueil
      </Link>
    </main>
  );
};

export default NotFound;
