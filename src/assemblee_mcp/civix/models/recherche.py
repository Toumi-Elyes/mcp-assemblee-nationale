"""Modèles de la recherche globale (les clés diffèrent de celles des autres points d'accès)."""

from datetime import datetime

from pydantic import Field

from assemblee_mcp.civix.models.base import CivixModel
from assemblee_mcp.civix.models.deputes import Depute


class DeputeSearchHit(CivixModel):
    """Député trouvé par la recherche globale (clés différentes de `/deputes`)."""

    uid: str = Field(alias="acteur_uid")
    prenom: str = ""
    nom: str = ""
    groupe_abrev: str | None = Field(default=None, alias="groupe_libelle_abrev")
    circ_departement: str | None = None
    slug: str | None = None

    def to_depute(self) -> Depute:
        """Convertit le résultat de recherche en `Depute`."""
        return Depute(
            uid=self.uid,
            prenom=self.prenom,
            nom=self.nom,
            groupe_abrev=self.groupe_abrev,
            circ_departement=self.circ_departement,
        )


class ScrutinSearchHit(CivixModel):
    """Scrutin trouvé par la recherche globale ; `type_vote` y est un simple texte."""

    uid: str
    titre: str = ""
    date_scrutin: datetime | None = None
    numero: int | None = None
    type_vote: str | None = None


class GroupeSearchHit(CivixModel):
    """Groupe trouvé par la recherche globale."""

    uid: str | None = None
    abbr: str
    libelle: str = ""


class DossierSearchHit(CivixModel):
    """Dossier législatif trouvé par la recherche globale."""

    uid: str
    titre: str = ""
    procedure_label: str | None = None


class SearchResultsByKind(CivixModel):
    """Résultats de recherche regroupés par type (8 au plus par type)."""

    deputes: list[DeputeSearchHit] = Field(default_factory=list)
    scrutins: list[ScrutinSearchHit] = Field(default_factory=list)
    groupes: list[GroupeSearchHit] = Field(default_factory=list)
    dossiers: list[DossierSearchHit] = Field(default_factory=list)


class SearchResults(CivixModel):
    """Attributs de `/search`."""

    query: str | None = None
    results: SearchResultsByKind = Field(default_factory=SearchResultsByKind)
    total: int = 0
