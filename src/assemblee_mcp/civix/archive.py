"""Index des législatures closes : députés et groupes que l'API CIVIX n'expose pas.

CIVIX publie les scrutins et les votes nominatifs des 14e, 15e et 16e législatures, mais
`/deputes?legislature=16` est vide, `/deputes/<uid>` répond 404 et `/groupes` ne liste que ceux de
la 17e. Les index embarqués (`data/legislature_<n>.json`, construits par
`scripts/build_legislature_data.py` à partir des données ouvertes de l'Assemblée nationale)
fournissent l'identifiant, le nom, le dernier groupe, le département et la circonscription de
chaque député, et le sigle de chaque groupe.
"""

import json
from dataclasses import dataclass
from datetime import date
from functools import cache
from importlib import resources

from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.limits import CURRENT_LEGISLATURE

DATA_PACKAGE = "assemblee_mcp.data"
DATA_FILE_PATTERN = "legislature_{number}.json"
ARCHIVED_LEGISLATURES = (16, 15, 14)
"""Législatures closes couvertes, de la plus récente à la plus ancienne."""


def covered_legislatures() -> str:
    """Législatures couvertes pour les députés, en toutes lettres (« 14e, 15e, 16e et 17e »)."""
    names = [f"{number}e" for number in sorted((*ARCHIVED_LEGISLATURES, CURRENT_LEGISLATURE))]
    return ", ".join(names[:-1]) + f" et {names[-1]}"


@dataclass(frozen=True)
class Membership:
    """Appartenance d'un député à un groupe, du jour `start` au jour `end` inclus."""

    groupe_uid: str
    start: date
    end: date | None

    def covers(self, day: date) -> bool:
        """Vrai si le député appartenait au groupe ce jour-là."""
        return self.start <= day and (self.end is None or day <= self.end)


@dataclass(frozen=True)
class Archive:
    """Députés, groupes et appartenances aux groupes d'une législature close."""

    legislature: int
    groupes: dict[str, Groupe]
    deputes: list[Depute]
    memberships: dict[str, tuple[Membership, ...]]

    def depute(self, uid: str) -> Depute | None:
        """Député d'identifiant `uid`, ou `None` s'il n'a pas siégé dans cette législature."""
        return next((depute for depute in self.deputes if depute.uid == uid), None)

    def group_at(self, uid: str, day: date) -> str | None:
        """Groupe du député ce jour-là (le plus récent en cas de changement le jour même)."""
        covering = [item for item in self.memberships.get(uid, ()) if item.covers(day)]
        return covering[-1].groupe_uid if covering else None

    def groups_for_vote(self, uid: str, day: date, published: set[str]) -> str | None:
        """Groupe du député à retenir pour un scrutin dont la ventilation cite `published`.

        D'abord son groupe ce jour-là ; s'il n'est pas dans la ventilation (CIVIX garde l'ancien
        identifiant d'un groupe renommé, comme les socialistes de la 16e en 2023), son groupe le
        plus récent qui y figure.
        """
        current = self.group_at(uid, day)
        if current in published:
            return current
        others = [item.groupe_uid for item in reversed(self.memberships.get(uid, ()))]
        return next((groupe for groupe in others if groupe in published), None)

    def members_at(self, groupe_uid: str, day: date) -> set[str]:
        """Identifiants des députés membres du groupe ce jour-là."""
        return {uid for uid in self.memberships if self.group_at(uid, day) == groupe_uid}


@cache
def load_archive(legislature: int) -> Archive | None:
    """Index d'une législature close, ou `None` si aucune n'est embarquée pour ce numéro."""
    if legislature not in ARCHIVED_LEGISLATURES:
        return None
    name = DATA_FILE_PATTERN.format(number=legislature)
    raw = json.loads(resources.files(DATA_PACKAGE).joinpath(name).read_text(encoding="utf-8"))
    groupes = {
        uid: Groupe(uid=uid, abbr=item["abbr"], libelle=item["libelle"], legislature=legislature)
        for uid, item in raw["groupes"].items()
    }
    rows: list[Row] = raw["deputes"]
    memberships = {row[0]: build_memberships(row[5]) for row in rows}
    deputes = [build_depute(row, groupes, legislature) for row in rows]
    return Archive(legislature, groupes, deputes, memberships)


type Row = tuple[str, str, str, str | None, int | None, list[tuple[str, str, str | None]]]
"""Ligne de l'index : `[uid, prénom, nom, département, circo, [[groupe, début, fin], …]]`."""


def build_memberships(spans: list[tuple[str, str, str | None]]) -> tuple[Membership, ...]:
    """Appartenances aux groupes, dans l'ordre chronologique de l'index."""
    return tuple(
        Membership(groupe_uid, date.fromisoformat(start), date.fromisoformat(end) if end else None)
        for groupe_uid, start, end in spans
    )


def build_depute(row: Row, groupes: dict[str, Groupe], legislature: int) -> Depute:
    """Député à partir d'une ligne de l'index ; son groupe est le dernier de la législature."""
    uid, first_name, last_name, departement, circo, spans = row
    groupe_uid = spans[-1][0] if spans else None
    groupe = groupes.get(groupe_uid) if groupe_uid else None
    return Depute(
        uid=uid,
        prenom=first_name,
        nom=last_name,
        legislature=legislature,
        circ_num=circo,
        circ_departement=departement,
        groupe_uid=groupe_uid,
        groupe_abrev=groupe.abbr if groupe else None,
        groupe_libelle=groupe.libelle if groupe else None,
    )
