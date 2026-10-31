"""Mise en forme des résultats de la recherche globale."""

from collections.abc import Callable
from datetime import date

from assemblee_mcp.civix.models import ScrutinSearchHit, SearchResultsByKind
from assemblee_mcp.civix.search import GlobalSearch
from assemblee_mcp.formatting.sources import finish, response_source_line
from assemblee_mcp.formatting.text import format_date, truncate
from assemblee_mcp.links import assemblee_dossier_url, scrutin_page_url

HIT_TITLE_LENGTH = 180
type SectionBuilder = Callable[[SearchResultsByKind], str | None]


def scrutin_section(results: SearchResultsByKind) -> str | None:
    """Section « Scrutins », ou `None` si aucun résultat."""
    if not results.scrutins:
        return None
    newest_first = sorted(results.scrutins, key=scrutin_sort_key, reverse=True)
    lines = "\n".join(
        f"- {format_date(hit.date_scrutin)} · {truncate(hit.titre, HIT_TITLE_LENGTH)} "
        f"· uid `{hit.uid}` · {scrutin_page_url(hit.uid, numero=hit.numero)}"
        for hit in newest_first
    )
    return f"### Scrutins (du plus récent au plus ancien)\n{lines}"


def depute_section(results: SearchResultsByKind) -> str | None:
    """Section « Députés », ou `None` si aucun résultat."""
    if not results.deputes:
        return None
    lines = "\n".join(
        f"- {hit.prenom} {hit.nom}"
        + (f" ({hit.groupe_abrev})" if hit.groupe_abrev else "")
        + f" · uid `{hit.uid}`"
        for hit in results.deputes
    )
    return f"### Députés\n{lines}"


def groupe_section(results: SearchResultsByKind) -> str | None:
    """Section « Groupes », ou `None` si aucun résultat."""
    if not results.groupes:
        return None
    lines = "\n".join(f"- {hit.abbr} : {hit.libelle}" for hit in results.groupes)
    return f"### Groupes\n{lines}"


def dossier_section(results: SearchResultsByKind) -> str | None:
    """Section « Dossiers législatifs », ou `None` si aucun résultat."""
    if not results.dossiers:
        return None
    lines = "\n".join(
        f"- {truncate(hit.titre, HIT_TITLE_LENGTH)} · dossier `{hit.uid}`"
        + (f" ({hit.procedure_label})" if hit.procedure_label else "")
        + (f" · {link}" if (link := assemblee_dossier_url(hit.uid)) else "")
        for hit in results.dossiers
    )
    hint = "Réutilisez la référence `DLR…` avec `dossier_legislatif` ou `positions_groupes`."
    return f"### Dossiers législatifs\n{lines}\n{hint}"


def scrutin_sort_key(hit: ScrutinSearchHit) -> tuple[date, int]:
    """Clé de tri chronologique d'un scrutin trouvé (date puis numéro)."""
    day = hit.date_scrutin.date() if hit.date_scrutin else date.min
    return day, hit.numero or 0


def section_builders(results: SearchResultsByKind) -> tuple[SectionBuilder, ...]:
    """Ordre des sections : députés d'abord pour une recherche de nom, sinon sujets d'abord."""
    if results.deputes:
        return (depute_section, scrutin_section, dossier_section, groupe_section)
    return (dossier_section, scrutin_section, groupe_section, depute_section)


def format_search(search: GlobalSearch, query: str) -> str:
    """Résultats de la recherche globale, par catégorie."""
    builders = section_builders(search.results)
    sections = [section for build in builders if (section := build(search.results)) is not None]
    lead = f"_{search.note}_\n\n" if search.note else ""
    source = response_source_line(search.response)
    if not sections:
        body = (
            f"{lead}Aucun résultat pour « {query} ». Essayez des mots-clés plus courts, "
            "avec les accents français."
        )
        return finish(body, source)
    note = (
        f"_{search.total} résultat(s) au total ; 8 au plus par catégorie. "
        "Pour en voir davantage, utilisez `rechercher_scrutins` ou `rechercher_deputes`._"
    )
    body = f"## Résultats pour « {query} »\n\n{lead}" + "\n\n".join(sections) + f"\n\n{note}"
    return finish(body, source)
