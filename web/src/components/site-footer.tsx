import { GITHUB_URL, LICENCE_URL } from "@/lib/config";
import { formatTimestamp } from "@/lib/format";

export const SiteFooter: React.FC<{ updatedAt: Date }> = ({ updatedAt }) => {
  return (
    <footer className="border-t border-line bg-surface-2">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-2">
        <div>
          <h2 className="text-lg font-semibold">Sources et neutralité</h2>
          <p className="mt-2 text-sm text-muted">
            Les données viennent des{" "}
            <a className="link" href="https://data.assemblee-nationale.fr">
              données ouvertes de l&apos;Assemblée nationale
            </a>
            , republiées par{" "}
            <a className="link" href="https://www.civix.fr">
              CIVIX
            </a>
            , une initiative indépendante et non officielle. Licence Ouverte Etalab 2.0.{" "}
            <a className="link" href={LICENCE_URL}>
              En savoir plus
            </a>
            .
          </p>
          <p className="mt-2 text-sm text-muted">
            Ce site affiche des faits et des liens vers les sources. Il ne classe pas les élus et n&apos;interprète
            aucun vote. Il n&apos;est affilié ni à l&apos;Assemblée nationale ni à CIVIX, et n&apos;utilise ni cookie ni
            outil de suivi.
          </p>
        </div>
        <div className="text-sm text-muted">
          <p>
            <a className="link" href={GITHUB_URL}>
              Code source sur GitHub
            </a>{" "}
            (licence MIT). Une erreur ou une idée ? Ouvrez une issue.
          </p>
          <p className="mt-2">
            Données rafraîchies toutes les 30 minutes au plus. Mis à jour le{" "}
            <time dateTime={updatedAt.toISOString()}>{formatTimestamp(updatedAt)}</time>.
          </p>
        </div>
      </div>
    </footer>
  );
};
