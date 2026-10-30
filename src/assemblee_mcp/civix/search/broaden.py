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


MIN_STEM_LENGTH = 5
"""Les mots plus courts (« loi », « prix », « voix ») sont gardés tels quels."""


def stem(word: str) -> str:
    """Racine d'un mot pour une recherche par sous-chaîne : sans marque du pluriel.

    CIVIX et l'archive cherchent une suite de lettres : « retraite » trouve « retraite » et
    « retraites », « hôpita » trouve « hôpital » et « hôpitaux ». Les accents sont gardés.
    """
    if len(word) < MIN_STEM_LENGTH:
        return word
    folded = word.casefold()
    if folded.endswith("aux"):
        return word[:-2]
    if folded.endswith(("s", "x")):
        return word[:-1]
    return word


def stem_query(query: str) -> str | None:
    """La requête avec chaque mot réduit à sa racine, ou `None` si rien ne change."""
    stemmed = WORD.sub(lambda match: stem(match.group(0)), query)
    return stemmed if stemmed != query else None


def stem_note(query: str, stemmed: str) -> str:
    """Phrase expliquant qu'une recherche au singulier a été utilisée."""
    return (
        f"Aucun résultat pour l'expression exacte « {query} » ; résultats pour « {stemmed} » "
        "(singulier et pluriel confondus)."
    )


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
