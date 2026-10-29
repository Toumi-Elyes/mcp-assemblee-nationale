"""Construction des liens publics vers CIVIX et l'Assemblée nationale."""

from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.urls import safe_url

CIVIX_SITE = "https://www.civix.fr"
ASSEMBLEE_DEPUTES = "https://www.assemblee-nationale.fr/dyn/deputes"


def civix_scrutin_url(uid: str) -> str:
    """Page CIVIX d'un scrutin."""
    return f"{CIVIX_SITE}/votes/{uid}"


def civix_depute_url(uid: str) -> str:
    """Page CIVIX d'un député."""
    return f"{CIVIX_SITE}/deputes/{uid}"


def civix_groupe_url(abbr: str) -> str:
    """Page CIVIX d'un groupe."""
    return f"{CIVIX_SITE}/groupes/{abbr}"


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
