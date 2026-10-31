export const AUDIENCE_KEY = "mesure-audience";

const REFUSED = "refusee";

type ReadableStorage = Pick<Storage, "getItem">;
type WritableStorage = Pick<Storage, "setItem" | "removeItem">;
type PrivacySignals = { globalPrivacyControl?: boolean };

/** Vrai si le navigateur envoie le signal Global Privacy Control (refus du suivi). */
export function sendsPrivacySignal(signals: PrivacySignals | null | undefined): boolean {
  return signals?.globalPrivacyControl === true;
}

/** Vrai si la personne a refusé la mesure d'audience sur ce site. */
export function hasRefused(storage: ReadableStorage | null | undefined): boolean {
  if (storage === null || storage === undefined) {
    return false;
  }
  try {
    return storage.getItem(AUDIENCE_KEY) === REFUSED;
  } catch {
    return false;
  }
}

/** Aucune mesure n'est envoyée si la personne l'a refusée ou si son navigateur envoie GPC. */
export function isMeasurementAllowed(
  storage: ReadableStorage | null | undefined,
  signals: PrivacySignals | null | undefined,
): boolean {
  return !hasRefused(storage) && !sendsPrivacySignal(signals);
}

export function storeRefusal(storage: WritableStorage | null | undefined, refused: boolean): void {
  if (storage === null || storage === undefined) {
    return;
  }
  try {
    if (refused) {
      storage.setItem(AUDIENCE_KEY, REFUSED);
    } else {
      storage.removeItem(AUDIENCE_KEY);
    }
  } catch {
    // Stockage indisponible (navigation privée stricte) : le choix vaut pour cette page seulement.
  }
}

export function browserStorage(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function browserSignals(): PrivacySignals {
  return navigator as Navigator & PrivacySignals;
}
