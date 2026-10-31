"use client";

import { useSyncExternalStore } from "react";
import { browserSignals, browserStorage, hasRefused, sendsPrivacySignal, storeRefusal } from "@/lib/audience";
import { BUTTON_SECONDARY_SMALL } from "./button-styles";

type Status = "loading" | "signal" | "refused" | "allowed";

const AUDIENCE_EVENT = "audience-change";

function subscribe(onChange: () => void): () => void {
  window.addEventListener("storage", onChange);
  window.addEventListener(AUDIENCE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(AUDIENCE_EVENT, onChange);
  };
}

function serverStatus(): Status {
  return "loading";
}

function currentStatus(): Status {
  if (sendsPrivacySignal(browserSignals())) {
    return "signal";
  }
  return hasRefused(browserStorage()) ? "refused" : "allowed";
}

const MESSAGES: Readonly<Record<Exclude<Status, "loading">, string>> = {
  signal:
    "Votre navigateur envoie le signal « Global Privacy Control » : vos visites ne sont pas mesurées.",
  refused: "Vous avez refusé la mesure : vos visites ne sont pas comptées sur ce navigateur.",
  allowed: "Vos visites sont comptées de façon anonyme. Vous pouvez le refuser à tout moment.",
};

export const AudienceChoice: React.FC = () => {
  const status = useSyncExternalStore(subscribe, currentStatus, serverStatus);

  if (status === "loading") {
    return null;
  }

  const toggle = () => {
    storeRefusal(browserStorage(), status === "allowed");
    window.dispatchEvent(new Event(AUDIENCE_EVENT));
  };

  return (
    <span className="flex flex-col items-start gap-3">
      <span role="status">{MESSAGES[status]}</span>
      {status === "signal" ? null : (
        <button type="button" onClick={toggle} className={BUTTON_SECONDARY_SMALL}>
          {status === "allowed" ? "Ne plus mesurer mes visites" : "Accepter de nouveau la mesure"}
        </button>
      )}
    </span>
  );
};
