"""Recherche globale par catégories (scrutins, dossiers, groupes, députés)."""

from collections import Counter
from dataclasses import dataclass

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.lookup import rank_by_name
from assemblee_mcp.civix.models import (
    DeputeSearchHit,
    DossierSearchHit,
    ScrutinSearchHit,
    ScrutinSummary,
    SearchResponse,
    SearchResultsByKind,
)
from assemblee_mcp.civix.search.broaden import broad_note, broaden, contains_all
from assemblee_mcp.civix.search.scrutins import search_scrutin_pool
from assemblee_mcp.limits import (
    SEARCH_CATEGORY_CAP,
)
from assemblee_mcp.textutils import tokens


@dataclass(frozen=True)
class GlobalSearch:
    """Résultat de la recherche globale, éventuellement élargie."""

    response: SearchResponse
    results: SearchResultsByKind
    total: int
    note: str | None = None


def count_hits(results: SearchResultsByKind) -> int:
    """Nombre total de résultats toutes catégories confondues."""
    return (
        len(results.deputes) + len(results.scrutins) + len(results.groupes) + len(results.dossiers)
    )


def only_named_deputes(results: SearchResultsByKind, query: str) -> SearchResultsByKind:
    """Retire les députés dont le nom ne contient pas les mots de la requête.

    CIVIX renvoie des députés approximatifs pour une expression de plusieurs mots (« projet de
    loi de finances » donne des noms sans rapport) : un député doit correspondre au nom cherché.
    """
    required = tuple(tokens(query))
    named = [hit for hit in results.deputes if contains_all(f"{hit.prenom} {hit.nom}", required)]
    return results.model_copy(update={"deputes": named})


def with_directory_deputes(
    client: CivixClient, results: SearchResultsByKind, query: str
) -> SearchResultsByKind:
    """Ajoute les députés de l'annuaire (s'il est en mémoire) quand `/search` n'en a trouvé aucun.

    `/search` ne retrouve pas certains noms accentués : l'annuaire en mémoire comble ce manque
    sans appel supplémentaire.
    """
    directory = client.directory.cached()
    if results.deputes or directory is None:
        return results
    hits = [
        DeputeSearchHit(
            uid=depute.uid,
            prenom=depute.prenom,
            nom=depute.nom,
            groupe_abrev=depute.groupe_abrev,
            circ_departement=depute.circ_departement,
        )
        for depute in rank_by_name(directory, query)[:SEARCH_CATEGORY_CAP]
    ]
    return results.model_copy(update={"deputes": hits})


def dossier_hits(items: list[ScrutinSummary]) -> list[DossierSearchHit]:
    """Dossiers législatifs (avec leur référence DLR…) des scrutins, du plus voté au moins voté."""
    titles: dict[str, str] = {}
    counts: Counter[str] = Counter()
    for item in items:
        if item.dossier_ref is not None:
            titles.setdefault(item.dossier_ref, item.dossier_libelle or item.dossier_ref)
            counts[item.dossier_ref] += 1
    return [
        DossierSearchHit(uid=reference, titre=titles[reference])
        for reference, _ in counts.most_common(SEARCH_CATEGORY_CAP)
    ]


def scrutin_hits(items: list[ScrutinSummary]) -> list[ScrutinSearchHit]:
    """Scrutins au format des résultats de la recherche globale (8 au plus)."""
    return [
        ScrutinSearchHit(
            uid=item.uid,
            titre=item.titre,
            date_scrutin=item.date_scrutin,
            numero=item.numero,
            type_vote=item.type_vote.libelle if item.type_vote else None,
        )
        for item in items[:SEARCH_CATEGORY_CAP]
    ]


async def search_everything(client: CivixClient, query: str, *, page: int = 1) -> GlobalSearch:
    """Recherche globale par catégories (au plus 8 appels CIVIX).

    On interroge `/search` avec la requête telle quelle. Une expression de plusieurs mots qui ne
    donne ni député correspondant, ni scrutin, ni dossier, ni groupe est élargie : scrutins et
    dossiers viennent alors de la recherche par mots (tous les mots exigés, sans accents).
    """
    exact = await client.search(query, page=page)
    results = with_directory_deputes(
        client, only_named_deputes(exact.attributes.results, query), query
    )
    broad = broaden(query)
    if broad is None or count_hits(results) > 0:
        return GlobalSearch(exact, results, count_hits(results))
    pool = await search_scrutin_pool(client, query)
    widened = SearchResultsByKind(
        scrutins=scrutin_hits(pool.items), dossiers=dossier_hits(pool.items)
    )
    note = broad_note(query, broad, truncated=pool.truncated)
    total = pool.matching + len(widened.dossiers)
    return GlobalSearch(exact, widened, total, note)
