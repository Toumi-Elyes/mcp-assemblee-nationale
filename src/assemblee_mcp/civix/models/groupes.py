"""Modèles des groupes parlementaires."""

from pydantic import Field

from assemblee_mcp.civix.models.base import CivixModel


class GroupeUrls(CivixModel):
    """Liens d'un groupe."""

    page: str | None = None
    api: str | None = None


class Groupe(CivixModel):
    """Un groupe parlementaire."""

    uid: str
    abbr: str
    libelle: str = ""
    legislature: int | None = None
    effectif: int | None = None
    urls: GroupeUrls | None = None


class GroupeList(CivixModel):
    """Liste des groupes (`/groupes`)."""

    groups: list[Groupe] = Field(default_factory=list)


class GroupeDetail(CivixModel):
    """Attributs de `/groupes/{abbr}`."""

    groupe: Groupe
