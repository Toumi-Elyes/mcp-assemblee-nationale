"use client";

import Link from "next/link";
import { ArrowClockwiseIcon, WarningCircleIcon } from "@phosphor-icons/react";
import { BUTTON_PRIMARY, BUTTON_SECONDARY } from "@/components/button-styles";

const ErrorPage: React.FC<{ error: Error; reset: () => void }> = ({ reset }) => {
  return (
    <main id="contenu" className="mx-auto flex w-full max-w-page flex-col items-start gap-6 px-4 pb-24 pt-12 sm:px-6">
      <WarningCircleIcon aria-hidden="true" size={32} weight="bold" />
      <h1 className="max-w-3xl font-display text-5xl font-semibold tracking-tight">Données momentanément indisponibles</h1>
      <p role="alert" className="max-w-measure text-lg text-ink-soft">
        La source des données ne répond pas pour le moment. Réessayez dans quelques minutes.
      </p>
      <div className="flex flex-wrap gap-3">
        <button type="button" onClick={reset} className={BUTTON_PRIMARY}>
          <ArrowClockwiseIcon aria-hidden="true" size={20} weight="bold" />
          Réessayer
        </button>
        <Link href="/" className={BUTTON_SECONDARY}>
          Retour à l'accueil
        </Link>
      </div>
    </main>
  );
};

export default ErrorPage;
