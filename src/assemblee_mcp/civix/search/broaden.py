"""Élargissement d'une requête de plusieurs mots : mots utiles, mot distinctif, filtre local."""

import re
from dataclasses import dataclass

from assemblee_mcp.civix.models import (
    ScrutinSummary,
)
from assemblee_mcp.limits import (
    BROAD_POOL_PAGES,
    CIVIX_PAGE_SIZE,
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


BROAD_POOL = CIVIX_PAGE_SIZE * BROAD_POOL_PAGES


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
