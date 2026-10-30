"""Scrutins des 14e et 15e législatures : titres, résultats et décomptes que CIVIX ne publie pas.

CIVIX publie ces scrutins et leurs votes nominatifs, mais sans titre, sans résultat et sans
décompte par groupe. Les fichiers embarqués `data/scrutins_<n>.json.gz` (construits par
`scripts/build_scrutin_data.py` à partir des archives de scrutins de l'Assemblée nationale)
complètent ses réponses ; ils servent aussi à chercher ces scrutins par mots-clés.

Pour 710 scrutins de la 14e législature (jusqu'en février 2014), l'Assemblée n'a publié que les
noms des députés ayant voté autrement que la position de leur groupe : leur liste de votes est
partielle, et le décompte officiel est celui de l'archive.
"""

import gzip
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import cache
from importlib import resources
from typing import Any

from assemblee_mcp.civix.models import (
    CivixResponse,
    Demandeur,
    GroupVoteCounts,
    Objet,
    Scrutin,
    ScrutinList,
    ScrutinSummary,
    Sort,
    TypeVote,
    VoteCounts,
)
from assemblee_mcp.civix.models.kinds import type_from_title
from assemblee_mcp.textutils import fold

DATA_PACKAGE = "assemblee_mcp.data"
DATA_FILE_PATTERN = "scrutins_{number}.json.gz"
COMPLETED_LEGISLATURES = (15, 14)
"""Législatures dont les scrutins sont complétés, de la plus récente à la plus ancienne."""
ARCHIVE_SOURCE = "https://data.assemblee-nationale.fr/travaux-parlementaires/votes"


@dataclass(frozen=True)
class ArchivedScrutin:
    """Ce que l'archive de l'Assemblée dit d'un scrutin."""

    uid: str
    legislature: int
    numero: int
    day: date
    titre: str
    sort_code: str
    type_vote: TypeVote
    demandeur: str | None
    dissidents_only: bool
    totals: VoteCounts
    groups: tuple[GroupVoteCounts, ...]

    def summary(self) -> ScrutinSummary:
        """Le scrutin sous la forme d'un élément de liste CIVIX."""
        return ScrutinSummary(
            uid=self.uid,
            legislature=self.legislature,
            numero=self.numero,
            date_scrutin=datetime(self.day.year, self.day.month, self.day.day, tzinfo=UTC),
            titre=self.titre,
            objet=Objet(libelle=self.titre),
            sort=Sort(code=self.sort_code),
            sort_code=self.sort_code,
            type_vote=self.type_vote,
            type=type_from_title(self.titre),
        )


def counts(values: list[int], groupe_uid: str | None = None) -> Any:
    """Décompte `[pour, contre, abstention, non_votant]`, par groupe si `groupe_uid` est donné."""
    pour, contre, abstention, non_votant = values
    fields = {
        "pour": pour,
        "contre": contre,
        "abstention": abstention,
        "non_votant": non_votant,
        "total": pour + contre + abstention + non_votant,
    }
    if groupe_uid is None:
        return VoteCounts(**fields)
    return GroupVoteCounts(groupe_uid=groupe_uid, **fields)


def build_scrutin(uid: str, legislature: int, row: list[Any]) -> ArchivedScrutin:
    """Scrutin d'après une ligne de l'archive embarquée."""
    day, titre, sort_code, type_libelle, majorite, demandeur, partial, totals, groups = row
    return ArchivedScrutin(
        uid=uid,
        legislature=legislature,
        numero=int(uid.rsplit("V", 1)[1]),
        day=date.fromisoformat(day),
        titre=titre,
        sort_code=sort_code,
        type_vote=TypeVote(libelle=type_libelle, type_majorite=majorite),
        demandeur=demandeur,
        dissidents_only=partial,
        totals=counts(totals),
        groups=tuple(counts(values, groupe_uid) for groupe_uid, *values in groups),
    )


@cache
def load_scrutins(legislature: int) -> dict[str, ArchivedScrutin] | None:
    """Scrutins archivés d'une législature, ou `None` si aucun fichier n'est embarqué pour elle."""
    if legislature not in COMPLETED_LEGISLATURES:
        return None
    name = DATA_FILE_PATTERN.format(number=legislature)
    raw = json.loads(gzip.decompress(resources.files(DATA_PACKAGE).joinpath(name).read_bytes()))
    return {uid: build_scrutin(uid, legislature, row) for uid, row in raw["scrutins"].items()}


def archived(uid: str, legislature: int | None) -> ArchivedScrutin | None:
    """Scrutin archivé d'identifiant `uid`, s'il existe."""
    scrutins = load_scrutins(legislature) if legislature is not None else None
    return scrutins.get(uid) if scrutins else None


def complete_summary(item: ScrutinSummary) -> ScrutinSummary:
    """Élément de liste complété par l'archive (titre, résultat, type), sinon inchangé."""
    found = archived(item.uid, item.legislature)
    if found is None or item.titre:
        return item
    return item.model_copy(
        update={
            "titre": found.titre,
            "objet": Objet(libelle=found.titre),
            "sort": Sort(code=found.sort_code),
            "sort_code": found.sort_code,
            "type_vote": found.type_vote,
            "type": type_from_title(found.titre),
        }
    )


def complete_scrutin[ScrutinT: Scrutin](attributes: ScrutinT) -> ScrutinT:
    """Détail complété par l'archive : titre, résultat, décomptes officiels global et par groupe."""
    scrutin = attributes.scrutin
    found = archived(scrutin.uid, scrutin.legislature)
    if found is None:
        return attributes
    detail = scrutin.model_copy(
        update={
            "titre": found.titre,
            "objet": Objet(libelle=found.titre),
            "sort_code": found.sort_code,
            "type_vote": found.type_vote,
            "majority_rule": found.type_vote.type_majorite,
            "demandeur": Demandeur(texte=found.demandeur) if found.demandeur else None,
        }
    )
    return attributes.model_copy(
        update={
            "scrutin": detail,
            "results_global": found.totals,
            "results_by_group": list(found.groups),
            "archived": True,
            "dissidents_only": found.dissidents_only,
        }
    )


def complete_response[ScrutinT: Scrutin](
    response: CivixResponse[ScrutinT],
) -> CivixResponse[ScrutinT]:
    """Réponse de détail ou de votes complétée par l'archive."""
    attributes = complete_scrutin(response.attributes)
    if attributes is response.attributes:
        return response
    return response.model_copy(
        update={"data": response.data.model_copy(update={"attributes": attributes})}
    )


def complete_list(response: CivixResponse[ScrutinList]) -> CivixResponse[ScrutinList]:
    """Liste de scrutins dont les éléments des 14e et 15e législatures sont complétés."""
    results = response.attributes.results
    completed = [complete_summary(item) for item in results]
    if all(new is old for new, old in zip(completed, results, strict=True)):
        return response
    attributes = response.attributes.model_copy(update={"results": completed})
    return response.model_copy(
        update={"data": response.data.model_copy(update={"attributes": attributes})}
    )


def search_archive(legislature: int, required: tuple[str, ...]) -> list[ScrutinSummary]:
    """Scrutins archivés dont le titre contient tous les mots `required`, du plus récent au plus
    ancien (accents et casse ignorés)."""
    scrutins = load_scrutins(legislature) or {}
    ordered = sorted(scrutins.values(), key=lambda item: item.numero, reverse=True)
    return [
        item.summary() for item in ordered if all(word in fold(item.titre) for word in required)
    ]
