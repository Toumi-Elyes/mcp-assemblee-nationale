import Link from "next/link";
import { ArrowLeftIcon } from "@phosphor-icons/react/dist/ssr";
import { BUTTON_PRIMARY } from "@/components/button-styles";
import { Flap } from "@/components/flap";

const NotFound: React.FC = () => {
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col items-start gap-6 px-4 pb-24 pt-12 sm:px-6">
      <Flap value="404" label="Erreur 404" className="text-7xl font-semibold" />
      <h1 className="max-w-3xl font-display text-5xl font-semibold tracking-tight">Cette page n'existe pas</h1>
      <p className="max-w-measure text-lg text-ink-soft">
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
