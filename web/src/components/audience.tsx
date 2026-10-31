"use client";

import { Analytics, type BeforeSendEvent } from "@vercel/analytics/next";

// Mesure d'audience sans cookie : on ne garde que le chemin de la page, jamais les paramètres.
function withoutQuery(event: BeforeSendEvent): BeforeSendEvent {
  const url = new URL(event.url);
  url.search = "";
  url.hash = "";
  return { ...event, url: url.toString() };
}

export const Audience: React.FC = () => {
  return <Analytics beforeSend={withoutQuery} />;
};
