"""Sources, pied de page et indications de pagination ajoutés à chaque réponse."""

from assemblee_mcp.civix.models import (
    CivixModel,
    CivixResponse,
    Pagination,
    ScrutinDetail,
)
from assemblee_mcp.links import assemblee_scrutin_url, civix_scrutin_url
from assemblee_mcp.urls import safe_url

FOOTER = (
    "_CIVIX est une interface indépendante et non officielle des données ouvertes "
    "de l'Assemblée nationale._"
)


def source_line(civix_url: str | None, assemblee_url: str | None) -> str:
    """Ligne « Source : » avec les liens disponibles."""
    parts = []
    if civix_url:
        parts.append(f"CIVIX {civix_url}")
    if assemblee_url:
        parts.append(f"Assemblée nationale {assemblee_url}")
    return "Source : " + (" — ".join(parts) if parts else "CIVIX https://www.civix.fr")


def response_source_line[AttributesT: CivixModel](response: CivixResponse[AttributesT]) -> str:
    """Ligne « Source : » d'une réponse CIVIX."""
    civix = response.source.civix_page or safe_url(response.canonical_url)
    return source_line(civix, response.source.assemblee_url)


def scrutin_source_line(scrutin: ScrutinDetail) -> str:
    """Ligne « Source : » d'un scrutin : sa page CIVIX et sa page à l'Assemblée nationale."""
    return source_line(
        civix_scrutin_url(scrutin.uid), assemblee_scrutin_url(scrutin.legislature, scrutin.numero)
    )


def finish(body: str, source: str) -> str:
    """Ajoute la ligne source et le pied de page à un corps de texte."""
    return f"{body}\n\n{source}\n{FOOTER}"


def pagination_hint(pagination: Pagination | None, shown: int, noun: str) -> str:
    """Indique s'il existe d'autres pages et comment les demander."""
    if pagination is None:
        return ""
    total = pagination.total
    count = f"{shown} {noun} affiché(s)" + (f" sur {total}" if total is not None else "")
    if pagination.next_page is None:
        return f"_{count}._"
    return (
        f"_{count} (page {pagination.page or 1}). Il reste des résultats : "
        f"demandez la page {pagination.next_page}._"
    )
