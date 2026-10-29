"""Recherche par mots-clés robuste.

CIVIX cherche une sous-chaîne exacte : « loi de finances 2027 » ne donne rien alors que
« loi de finances pour 2027 » donne des résultats. On essaie donc d'abord la requête telle
quelle ; sans résultat, on interroge CIVIX avec le mot le plus distinctif puis on filtre
localement sur tous les autres mots, sans tenir compte des accents ni de la casse.
"""

import re
from dataclasses import dataclass

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import (
    Pagination,
    ScrutinListResponse,
    ScrutinSummary,
    SearchResponse,
    SearchResultsByKind,
)
from assemblee_mcp.textutils import fold

STOPWORDS = frozenset(
    [
        "de",
        "du",
        "des",
        "la",
        "le",
        "les",
        "l",
        "d",
        "pour",
        "sur",
        "et",
        "a",
        "au",
        "aux",
        "en",
        "un",
        "une",
        "qui",
        "que",
        "dans",
        "par",
        "ce",
        "cet",
        "cette",
        "ces",
    ]
)
MIN_WORDS = 2
WEAK_WORDS = frozenset({"loi"})
YEAR = re.compile(r"\d{4}")
WORD = re.compile(r"\w+")
BROAD_PAGE_SIZE = 50
BROAD_MAX_PAGES = 2
BROAD_POOL = BROAD_PAGE_SIZE * BROAD_MAX_PAGES


@dataclass(frozen=True)
class BroadQuery:
    """Requête élargie : mot interrogé chez CIVIX et mots exigés localement."""

    term: str
    required: tuple[str, ...]


def broaden(query: str) -> BroadQuery | None:
    """Prépare une recherche élargie ; `None` si la requête n'a pas plusieurs mots utiles."""
    words = WORD.findall(query.casefold())
    if len(words) < MIN_WORDS:
        return None
    kept = [word for word in words if fold(word) not in STOPWORDS]
    years = [word for word in kept if YEAR.fullmatch(word)]
    content = [word for word in kept if not YEAR.fullmatch(word)]
    strong = [word for word in content if word not in WEAK_WORDS]
    content = strong or content
    if content:
        term = max(content, key=len)
    elif years:
        term = years[0]
    else:
        return None
    required = tuple(dict.fromkeys(fold(word) for word in (*content, *years)))
    return BroadQuery(term=term, required=required)


def contains_all(text: str, required: tuple[str, ...]) -> bool:
    """Vrai si le texte contient tous les mots exigés (accents et casse ignorés)."""
    folded = fold(text)
    return all(word in folded for word in required)


def broad_note(query: str, broad: BroadQuery, *, truncated: bool) -> str:
    """Phrase expliquant qu'une recherche élargie a été utilisée."""
    words = ", ".join(f"« {word} »" for word in broad.required)
    note = (
        f"Recherche élargie : aucun résultat pour l'expression exacte « {query} » ; "
        f"résultats contenant tous les mots {words}."
    )
    if truncated:
        note += f" Analyse limitée aux {BROAD_POOL} scrutins les plus récents."
    return note


def summary_text(scrutin: ScrutinSummary) -> str:
    """Texte sur lequel porte le filtre local d'un scrutin."""
    parts = [scrutin.titre]
    if scrutin.objet:
        parts.append(scrutin.objet.libelle or "")
        if scrutin.objet.dossier_legislatif:
            parts.append(scrutin.objet.dossier_legislatif.libelle or "")
    return " ".join(parts)


@dataclass(frozen=True)
class ScrutinSearch:
    """Résultat d'une recherche de scrutins, éventuellement élargie."""

    response: ScrutinListResponse
    results: list[ScrutinSummary]
    pagination: Pagination | None
    note: str | None = None


def scrutins_empty(response: ScrutinListResponse) -> bool:
    """Vrai si CIVIX n'a trouvé aucun scrutin."""
    pagination = response.pagination
    return not response.attributes.results and (pagination is None or not pagination.total)


async def search_scrutins(
    client: CivixClient,
    query: str | None,
    *,
    legislature: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> ScrutinSearch:
    """Cherche des scrutins (au plus 3 appels CIVIX)."""
    exact = await client.list_scrutins(
        query, legislature=legislature, page=page, page_size=page_size
    )
    broad = broaden(query) if query else None
    if broad is None or not scrutins_empty(exact):
        return ScrutinSearch(exact, list(exact.attributes.results), exact.pagination)
    pool, truncated = await broad_pool(client, broad, legislature)
    matches = [s for s in pool if contains_all(summary_text(s), broad.required)]
    start = (page - 1) * page_size
    shown = matches[start : start + page_size]
    pagination = Pagination(
        page=page,
        page_size=page_size,
        next_page=page + 1 if start + page_size < len(matches) else None,
        count_total=len(matches),
    )
    return ScrutinSearch(
        exact, shown, pagination, broad_note(query or "", broad, truncated=truncated)
    )


async def broad_pool(
    client: CivixClient, broad: BroadQuery, legislature: int | None
) -> tuple[list[ScrutinSummary], bool]:
    """Scrutins contenant le mot distinctif (2 pages de 50 au plus), du plus récent."""
    pool: list[ScrutinSummary] = []
    truncated = False
    for page in range(1, BROAD_MAX_PAGES + 1):
        response = await client.list_scrutins(
            broad.term, legislature=legislature, page=page, page_size=BROAD_PAGE_SIZE
        )
        pool.extend(response.attributes.results)
        has_next = response.pagination is not None and response.pagination.next_page is not None
        if not has_next:
            return pool, False
        truncated = True
    return pool, truncated


@dataclass(frozen=True)
class GlobalSearch:
    """Résultat de la recherche globale, éventuellement élargie."""

    response: SearchResponse
    results: SearchResultsByKind
    total: int
    note: str | None = None


async def search_everything(client: CivixClient, query: str, *, page: int = 1) -> GlobalSearch:
    """Recherche globale (au plus 3 appels CIVIX)."""
    exact = await client.search(query, page=page)
    attributes = exact.attributes
    broad = broaden(query)
    if broad is None or exact.attributes.total > 0:
        return GlobalSearch(exact, attributes.results, attributes.total)
    deputes, scrutins, groupes, dossiers = [], [], [], []
    for pool_page in range(1, BROAD_MAX_PAGES + 1):
        found = (await client.search(broad.term, page=pool_page)).attributes.results
        deputes += found.deputes
        scrutins += found.scrutins
        groupes += found.groupes
        dossiers += found.dossiers
        if not any((found.deputes, found.scrutins, found.groupes, found.dossiers)):
            break
    required = broad.required
    results = SearchResultsByKind(
        deputes=[d for d in deputes if contains_all(f"{d.prenom} {d.nom}", required)],
        scrutins=[s for s in scrutins if contains_all(s.titre, required)],
        groupes=[g for g in groupes if contains_all(f"{g.abbr} {g.libelle}", required)],
        dossiers=[d for d in dossiers if contains_all(d.titre, required)],
    )
    total = (
        len(results.deputes) + len(results.scrutins) + len(results.groupes) + len(results.dossiers)
    )
    return GlobalSearch(exact, results, total, broad_note(query, broad, truncated=False))
