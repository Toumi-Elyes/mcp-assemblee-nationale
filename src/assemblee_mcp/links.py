"""Construction des liens publics vers CIVIX et l'Assemblée nationale."""

import re

from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.urls import safe_url

CIVIX_SITE = "https://www.civix.fr"
ASSEMBLEE_DEPUTES = "https://www.assemblee-nationale.fr/dyn/deputes"
ASSEMBLEE_SCRUTINS = "https://www.assemblee-nationale.fr/dyn"


def civix_scrutin_url(uid: str) -> str:
    """Page CIVIX d'un scrutin."""
    return f"{CIVIX_SITE}/votes/{uid}"


def civix_depute_url(uid: str) -> str:
    """Page CIVIX d'un député."""
    return f"{CIVIX_SITE}/deputes/{uid}"


def civix_groupe_url(abbr: str) -> str:
    """Page CIVIX d'un groupe."""
    return f"{CIVIX_SITE}/groupes/{abbr}"


def assemblee_scrutin_url(legislature: int | None, numero: int | None) -> str | None:
    """Page d'un scrutin sur le site de l'Assemblée nationale, construite ici.

    L'adresse publiée par CIVIX (`.../scrutins/jo9231`) renvoie une erreur 404 ; la page existe
    en `.../dyn/<législature>/scrutins/<numéro>`. Sans l'un des deux, on n'en donne pas.
    """
    if legislature is None or numero is None:
        return None
    return f"{ASSEMBLEE_SCRUTINS}/{legislature}/scrutins/{numero}"


SCRUTIN_UID = re.compile(r"^VTANR5L(\d{1,2})V(\d{1,6})$")


def scrutin_page_url(uid: str, legislature: int | None = None, numero: int | None = None) -> str:
    """Lien à citer pour un scrutin : sa page à l'Assemblée nationale, sinon sa page CIVIX.

    L'identifiant `VTANR5L17V9231` contient la législature (17) et le numéro (9231) : il suffit
    quand l'un des deux manque. Chaque scrutin cité dans une réponse porte ce lien, pour que
    l'assistant n'ait jamais à construire une adresse lui-même.
    """
    if legislature is None or numero is None:
        found = SCRUTIN_UID.match(uid)
        if found is not None:
            legislature, numero = int(found.group(1)), int(found.group(2))
    return assemblee_scrutin_url(legislature, numero) or civix_scrutin_url(uid)


DOSSIER_REFERENCE = re.compile(r"^DLR5L(\d{1,2})N\d{3,8}$")


def assemblee_dossier_url(reference: str) -> str | None:
    """Page d'un dossier législatif sur le site de l'Assemblée nationale.

    La référence `DLR5L17N54629` contient la législature (17) ; la page existe en
    `.../dyn/17/dossiers/DLR5L17N54629`. Une référence d'une autre forme n'a pas d'adresse.
    """
    found = DOSSIER_REFERENCE.match(reference)
    if found is None:
        return None
    return f"{ASSEMBLEE_SCRUTINS}/{found.group(1)}/dossiers/{reference}"


def assemblee_depute_url(uid: str) -> str:
    """Fiche d'un député sur le site de l'Assemblée nationale."""
    return f"{ASSEMBLEE_DEPUTES}/{uid}"


def depute_civix_url(depute: Depute) -> str:
    """Lien CIVIX d'un député."""
    given = depute.urls.civix_page if depute.urls else None
    return safe_url(given, civix_depute_url(depute.uid)) or civix_depute_url(depute.uid)


def depute_assemblee_url(depute: Depute) -> str:
    """Lien Assemblée nationale d'un député."""
    given = depute.urls.assemblee if depute.urls else None
    return safe_url(given, assemblee_depute_url(depute.uid)) or assemblee_depute_url(depute.uid)


def groupe_civix_url(groupe: Groupe) -> str:
    """Lien CIVIX d'un groupe."""
    given = groupe.urls.page if groupe.urls else None
    return safe_url(given, civix_groupe_url(groupe.abbr)) or civix_groupe_url(groupe.abbr)
