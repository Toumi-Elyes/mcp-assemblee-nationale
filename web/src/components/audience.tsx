"use client";

import { Analytics, type BeforeSendEvent } from "@vercel/analytics/next";
import { browserSignals, browserStorage, isMeasurementAllowed } from "@/lib/audience";

// Mesure d'audience sans cookie : on ne garde que le chemin de la page, jamais les paramètres,
// et rien n'est envoyé si la personne a refusé la mesure ou si son navigateur envoie GPC.
function beforeSend(event: BeforeSendEvent): BeforeSendEvent | null {
  if (!isMeasurementAllowed(browserStorage(), browserSignals())) {
    return null;
  }
  const url = new URL(event.url);
  url.search = "";
  url.hash = "";
  return { ...event, url: url.toString() };
}

export const Audience: React.FC = () => {
  return <Analytics beforeSend={beforeSend} />;
};
