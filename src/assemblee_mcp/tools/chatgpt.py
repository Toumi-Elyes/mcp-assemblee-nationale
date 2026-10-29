"""Outils `search` et `fetch` attendus par ChatGPT (deep research et connecteurs)."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.formatting import (
    format_date,
    format_depute,
    format_groupe,
    format_scrutin,
    truncate,
)
from assemblee_mcp.links import civix_depute_url, civix_groupe_url, civix_scrutin_url
from assemblee_mcp.tools.common import READ_ONLY_ANNOTATIONS, civix_tool

SCRUTIN_PREFIX = "scrutin"
DEPUTE_PREFIX = "depute"
GROUPE_PREFIX = "groupe"
ID_SEPARATOR = ":"
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
    """Sépare `<type>:<valeur>` ; lève `ToolError` si le format est invalide."""
    prefix, separator, value = identifier.partition(ID_SEPARATOR)
    if not separator or not value:
        raise ToolError(
            "Identifiant invalide : attendu « scrutin:<uid> », « depute:<uid> » ou « groupe:<sigle> »."
        )
    if prefix not in {SCRUTIN_PREFIX, DEPUTE_PREFIX, GROUPE_PREFIX}:
        raise ToolError(f"Type d'identifiant inconnu : « {prefix} ».")
    return prefix, value


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre `search` et `fetch`."""

    @civix_tool
    async def search(
        query: Annotated[
            str,
            Field(
                description="Mots-clés : sujet de vote, nom de député ou de groupe.",
                min_length=2,
                max_length=200,
            ),
        ],
    ) -> str:
        """Cherche des scrutins, députés et groupes de l'Assemblée nationale (données CIVIX).

        Renvoie un JSON `{"results": [{"id", "title", "url"}]}` ; les identifiants
        (`scrutin:<uid>`, `depute:<uid>`, `groupe:<sigle>`) se passent à `fetch`.
        """
        results = (await client.search(query)).attributes.results
        items = [
            SearchItem(
                id=make_id(SCRUTIN_PREFIX, hit.uid),
                title=truncate(f"Scrutin du {format_date(hit.date_scrutin)} — {hit.titre}", 200),
                url=civix_scrutin_url(hit.uid),
            )
            for hit in results.scrutins
        ]
        items += [
            SearchItem(
                id=make_id(DEPUTE_PREFIX, hit.uid),
                title=f"Député : {hit.prenom} {hit.nom}"
                + (f" ({hit.groupe_abrev})" if hit.groupe_abrev else ""),
                url=civix_depute_url(hit.uid),
            )
            for hit in results.deputes
        ]
        items += [
            SearchItem(
                id=make_id(GROUPE_PREFIX, hit.abbr),
                title=f"Groupe : {hit.libelle} ({hit.abbr})",
                url=civix_groupe_url(hit.abbr),
            )
            for hit in results.groupes
        ]
        return SearchPayload(results=items).model_dump_json()

    @civix_tool
    async def fetch(
        id: Annotated[
            str,
            Field(
                description="Identifiant renvoyé par `search` : scrutin:<uid>, depute:<uid>, groupe:<sigle>.",
                min_length=3,
                max_length=100,
            ),
        ],
    ) -> str:
        """Récupère le contenu complet d'un résultat de `search` (scrutin, député ou groupe).

        Renvoie un JSON `{"id", "title", "text", "url", "metadata"}` ; `text` est du markdown
        français avec décomptes, sources et liens.
        """
        prefix, value = split_id(id)
        if prefix == SCRUTIN_PREFIX:
            payload = await fetch_scrutin(client, value)
        elif prefix == DEPUTE_PREFIX:
            payload = await fetch_depute(client, value)
        else:
            payload = await fetch_groupe(client, value)
        return payload.model_dump_json()

    for function in (search, fetch):
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)


async def fetch_scrutin(client: CivixClient, uid: str) -> FetchPayload:
    """Contenu d'un scrutin pour `fetch`."""
    response, groups = await asyncio.gather(
        client.get_scrutin(uid), lookup.groupe_abbreviations(client)
    )
    scrutin = response.attributes.scrutin
    return FetchPayload(
        id=make_id(SCRUTIN_PREFIX, scrutin.uid),
        title=truncate(f"Scrutin n°{scrutin.numero} — {scrutin.titre}", 200),
        text=format_scrutin(response, groups),
        url=civix_scrutin_url(scrutin.uid),
        metadata={
            "type": SCRUTIN_PREFIX,
            "date": scrutin.date_scrutin.date().isoformat() if scrutin.date_scrutin else None,
            "legislature": scrutin.legislature,
            "numero": scrutin.numero,
            "resultat": scrutin.result_label,
            "adopte": scrutin.is_adopted,
            "source_assemblee": response.source.assemblee_url,
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
