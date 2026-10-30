"""Analyse d'un dossier législatif : chronologie de ses scrutins et méthode associée.

Partagée par l'outil `dossier_legislatif` et par `fetch` (ChatGPT) pour un `dossier:<DLR…>`.
"""

from dataclasses import dataclass

from assemblee_mcp.analytics import gather, stats
from assemblee_mcp.analytics.models import DossierTimeline, Method, TextActivity
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.search import ScrutinPool, search_scrutin_pool


@dataclass(frozen=True)
class DossierAnalysis:
    """Chronologie d'un dossier et la méthode qui la décrit."""

    timeline: DossierTimeline
    method: Method


def choose_dossier(ranked: list[TextActivity], query: str) -> TextActivity:
    """Dossier détaillé : celui dont la référence est `query`, sinon le plus voté."""
    return next((row for row in ranked if row.dossier_ref == query), ranked[0])


def timeline_method(total: int, shown: int, pool: ScrutinPool) -> Method:
    """Méthode de la chronologie d'un dossier."""
    return Method(
        analysed=shown,
        matching=total,
        truncated=total > shown,
        counted=(
            "tous les scrutins publics rattachés au dossier ; amendements comptés, autres "
            "scrutins listés du plus ancien au plus récent."
        ),
        limits=["les votes sur l'ensemble sont ceux de type « texte » dans CIVIX."],
        notes=[f"Recherche du dossier. {pool.note}"] if pool.note else [],
    )


async def analyse_dossier(client: CivixClient, query: str) -> DossierAnalysis | None:
    """Chronologie du dossier correspondant à `query` (mots-clés ou référence DLR…).

    Renvoie `None` si aucun scrutin ne correspond. Si plusieurs dossiers correspondent, le plus
    voté (ou celui dont la référence est `query`) est détaillé et les autres sont proposés.
    """
    pool = await search_scrutin_pool(client, query)
    if not pool.items:
        return None
    ranked = stats.rank_texts(pool.items)
    chosen = choose_dossier(ranked, query)
    others = [row for row in ranked if row.dossier_ref != chosen.dossier_ref]
    items, total = await gather.fetch_dossier_scrutins(
        client, chosen.dossier_ref, chosen.libelle, pool.items
    )
    timeline = stats.dossier_timeline(items, others)
    return DossierAnalysis(timeline, timeline_method(total, len(items), pool))
