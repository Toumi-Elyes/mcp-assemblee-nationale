"""Contenus JSON des outils `search` et `fetch` de ChatGPT : identifiants, modèles et documents."""

import asyncio
import re

from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from assemblee_mcp.analytics.dossier import analyse_dossier
from assemblee_mcp.analytics.models import DossierTimeline
from assemblee_mcp.analytics.render import render_timeline
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import SearchResultsByKind
from assemblee_mcp.formatting import (
    format_date,
    format_depute,
    format_groupe,
    format_scrutin,
    truncate,
)
from assemblee_mcp.links import (
    assemblee_dossier_url,
    assemblee_scrutin_url,
    civix_depute_url,
    civix_groupe_url,
    civix_scrutin_url,
)

SEARCH_TITLE_LENGTH = 200
SCRUTIN_PREFIX = "scrutin"
DEPUTE_PREFIX = "depute"
GROUPE_PREFIX = "groupe"
DOSSIER_PREFIX = "dossier"
ID_SEPARATOR = ":"
ID_PATTERNS = {
    SCRUTIN_PREFIX: re.compile(r"[A-Za-z0-9_-]{3,64}"),
    DEPUTE_PREFIX: re.compile(r"[A-Za-z0-9]{3,32}"),
    GROUPE_PREFIX: re.compile(r"[A-Za-z0-9_-]{1,32}"),
    DOSSIER_PREFIX: re.compile(r"DLR5L\d{1,2}N\d{3,8}"),
}
Metadata = dict[str, str | int | bool | None]


class SearchItem(BaseModel):
    """Un résultat de `search`."""

    id: str
    title: str
    url: str


class SearchPayload(BaseModel):
    """Charge utile JSON de `search`."""

    results: list[SearchItem]


class FetchPayload(BaseModel):
    """Charge utile JSON de `fetch`."""

    id: str
    title: str
    text: str
    url: str
    metadata: Metadata


def make_id(prefix: str, value: str) -> str:
    """Identifiant `<type>:<valeur>` utilisé par search et fetch."""
    return f"{prefix}{ID_SEPARATOR}{value}"


def split_id(identifier: str) -> tuple[str, str]:
    """Sépare `<type>:<valeur>` et valide la valeur ; lève `ToolError` si invalide."""
    prefix, separator, value = identifier.partition(ID_SEPARATOR)
    if not separator or not value:
        raise ToolError(
            "Identifiant invalide : attendu « scrutin:<uid> », « depute:<uid> », "
            "« groupe:<sigle> » ou « dossier:<DLR…> »."
        )
    pattern = ID_PATTERNS.get(prefix)
    if pattern is None:
        raise ToolError(f"Type d'identifiant inconnu : « {prefix} ».")
    if pattern.fullmatch(value) is None:
        raise ToolError(f"Identifiant invalide pour le type « {prefix} » : « {value[:40]} ».")
    return prefix, value


def scrutin_items(results: SearchResultsByKind) -> list[SearchItem]:
    """Résultats `search` pour les scrutins."""
    return [
        SearchItem(
            id=make_id(SCRUTIN_PREFIX, hit.uid),
            title=truncate(
                f"Scrutin du {format_date(hit.date_scrutin)} — {hit.titre}", SEARCH_TITLE_LENGTH
            ),
            url=civix_scrutin_url(hit.uid),
        )
        for hit in results.scrutins
    ]


def depute_items(results: SearchResultsByKind) -> list[SearchItem]:
    """Résultats `search` pour les députés."""
    return [
        SearchItem(
            id=make_id(DEPUTE_PREFIX, hit.uid),
            title=f"Député : {hit.prenom} {hit.nom}"
            + (f" ({hit.groupe_abrev})" if hit.groupe_abrev else ""),
            url=civix_depute_url(hit.uid),
        )
        for hit in results.deputes
    ]


def groupe_items(results: SearchResultsByKind) -> list[SearchItem]:
    """Résultats `search` pour les groupes."""
    return [
        SearchItem(
            id=make_id(GROUPE_PREFIX, hit.abbr),
            title=f"Groupe : {hit.libelle} ({hit.abbr})",
            url=civix_groupe_url(hit.abbr),
        )
        for hit in results.groupes
    ]


def dossier_items(results: SearchResultsByKind) -> list[SearchItem]:
    """Résultats `search` pour les dossiers législatifs (ceux dont la page existe)."""
    items: list[SearchItem] = []
    for hit in results.dossiers:
        url = assemblee_dossier_url(hit.uid)
        if url is not None:
            title = truncate(f"Dossier : {hit.titre}", SEARCH_TITLE_LENGTH)
            items.append(SearchItem(id=make_id(DOSSIER_PREFIX, hit.uid), title=title, url=url))
    return items


def search_items(results: SearchResultsByKind) -> list[SearchItem]:
    """Résultats de `search` : députés d'abord pour un nom, sinon dossiers puis scrutins."""
    if results.deputes:
        parts = (depute_items, scrutin_items, dossier_items, groupe_items)
    else:
        parts = (dossier_items, scrutin_items, groupe_items, depute_items)
    return [item for build in parts for item in build(results)]


async def fetch_document(client: CivixClient, identifier: str) -> FetchPayload:
    """Document complet correspondant à un identifiant renvoyé par `search`."""
    prefix, value = split_id(identifier)
    if prefix == SCRUTIN_PREFIX:
        return await fetch_scrutin(client, value)
    if prefix == DEPUTE_PREFIX:
        return await fetch_depute(client, value)
    if prefix == DOSSIER_PREFIX:
        return await fetch_dossier(client, value)
    return await fetch_groupe(client, value)


async def fetch_scrutin(client: CivixClient, uid: str) -> FetchPayload:
    """Contenu d'un scrutin pour `fetch`."""
    response, groups = await asyncio.gather(
        client.get_scrutin(uid), lookup.groupe_abbreviations(client)
    )
    scrutin = response.attributes.scrutin
    return FetchPayload(
        id=make_id(SCRUTIN_PREFIX, scrutin.uid),
        title=truncate(f"Scrutin n°{scrutin.numero} — {scrutin.titre}", SEARCH_TITLE_LENGTH),
        text=format_scrutin(response, groups),
        url=civix_scrutin_url(scrutin.uid),
        metadata={
            "type": SCRUTIN_PREFIX,
            "date": scrutin.date_scrutin.date().isoformat() if scrutin.date_scrutin else None,
            "legislature": scrutin.legislature,
            "numero": scrutin.numero,
            "resultat": scrutin.result_label,
            "adopte": scrutin.is_adopted,
            "source_assemblee": assemblee_scrutin_url(scrutin.legislature, scrutin.numero),
        },
    )


async def fetch_depute(client: CivixClient, uid: str) -> FetchPayload:
    """Contenu d'un député pour `fetch`."""
    response = await client.get_depute(uid.upper())
    depute = response.attributes.deputy
    return FetchPayload(
        id=make_id(DEPUTE_PREFIX, depute.uid),
        title=depute.full_name,
        text=format_depute(response),
        url=civix_depute_url(depute.uid),
        metadata={
            "type": DEPUTE_PREFIX,
            "groupe": depute.groupe_abrev,
            "departement": depute.circ_departement,
            "legislature": depute.legislature,
            "source_assemblee": response.source.assemblee_url,
        },
    )


async def fetch_groupe(client: CivixClient, abbr: str) -> FetchPayload:
    """Contenu d'un groupe pour `fetch`."""
    found = await lookup.find_groupe(client, abbr)
    if found is None:
        raise ToolError(f"Groupe « {abbr} » inconnu.")
    response = await client.get_groupe(found.abbr)
    groupe = response.attributes.groupe
    return FetchPayload(
        id=make_id(GROUPE_PREFIX, groupe.abbr),
        title=f"{groupe.libelle} ({groupe.abbr})",
        text=format_groupe(response),
        url=civix_groupe_url(groupe.abbr),
        metadata={
            "type": GROUPE_PREFIX,
            "effectif": groupe.effectif,
            "legislature": groupe.legislature,
        },
    )


async def fetch_dossier(client: CivixClient, reference: str) -> FetchPayload:
    """Chronologie d'un dossier législatif pour `fetch` (même analyse que `dossier_legislatif`)."""
    url = assemblee_dossier_url(reference) or civix_scrutin_url(reference)
    analysis = await analyse_dossier(client, reference)
    if analysis is None or analysis.timeline.dossier_ref != reference:
        return dossier_without_scrutin(reference, url)
    timeline = analysis.timeline
    return FetchPayload(
        id=make_id(DOSSIER_PREFIX, reference),
        title=truncate(f"Dossier : {timeline.libelle}", SEARCH_TITLE_LENGTH),
        text=render_timeline(timeline, analysis.method),
        url=url,
        metadata={
            "type": DOSSIER_PREFIX,
            "reference": reference,
            "contexte": timeline.context,
            "scrutins": timeline.total,
            "amendements": timeline.amendements.total,
            "amendements_adoptes": timeline.amendements.adopted,
            "amendements_rejetes": timeline.amendements.rejected,
            "votes_sur_l_ensemble": len(timeline.final_votes),
            "dernier_vote_sur_l_ensemble": dernier_vote(timeline),
            "source_assemblee": url,
        },
    )


def dossier_without_scrutin(reference: str, url: str) -> FetchPayload:
    """Document d'un dossier sans scrutin public rattaché (résolution, texte jamais voté…)."""
    text = (
        f"## Dossier `{reference}`\n\nAucun scrutin public n'est rattaché à ce dossier dans "
        "CIVIX : il n'a pas donné lieu à un vote nominatif, ou la référence est inexacte. "
        f"Si elle est correcte, la page de l'Assemblée nationale détaille le dossier : {url}"
    )
    return FetchPayload(
        id=make_id(DOSSIER_PREFIX, reference),
        title=f"Dossier {reference} (aucun scrutin public)",
        text=text,
        url=url,
        metadata={"type": DOSSIER_PREFIX, "reference": reference, "scrutins": 0},
    )


def dernier_vote(timeline: DossierTimeline) -> str | None:
    """Résultat du dernier vote sur l'ensemble du texte, ou `None` s'il n'y en a pas."""
    if not timeline.final_votes:
        return None
    last = timeline.final_votes[-1]
    day = last.day.isoformat() if last.day else "date inconnue"
    return f"{day} : {last.result}"
