"""Résolution d'un nom de député en un député précis, partagée par plusieurs outils."""

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Depute
from assemblee_mcp.formatting import format_depute_candidates, format_deputes

MAX_CANDIDATES = 10


def pick_depute(candidates: list[Depute], query: str) -> Depute | None:
    """Choisit le député visé : unique résultat, ou unique correspondance exacte du nom."""
    if len(candidates) == 1:
        return candidates[0]
    exact = [depute for depute in candidates if lookup.is_exact_name(depute, query)]
    return exact[0] if len(exact) == 1 else None


async def resolve_depute(client: CivixClient, name: str) -> Depute | str:
    """Député visé, ou texte de réponse si le nom est introuvable ou ambigu."""
    candidates = await lookup.find_deputes(client, name)
    if not candidates:
        return format_deputes([], f"Député « {name} »")
    chosen = pick_depute(candidates, name)
    if chosen is None:
        return format_depute_candidates(name, candidates, MAX_CANDIDATES)
    return chosen
