"""Modèles des scrutins : liste, détail, décomptes, votes individuels et déclarations de groupes."""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from assemblee_mcp.civix.models.base import CivixModel, Position
from assemblee_mcp.civix.models.kinds import classify_scrutin


class Sort(CivixModel):
    """Résultat officiel d'un scrutin."""

    code: str | None = None
    libelle: str | None = None


class DossierLegislatif(CivixModel):
    """Dossier législatif rattaché à un scrutin."""

    libelle: str | None = None
    dossier_ref: str | None = Field(default=None, alias="dossierRef")


class Objet(CivixModel):
    """Objet d'un scrutin."""

    libelle: str | None = None
    dossier_legislatif: DossierLegislatif | None = Field(default=None, alias="dossierLegislatif")


class TypeVote(CivixModel):
    """Type de vote (scrutin public ordinaire, solennel…)."""

    code: str | None = Field(default=None, alias="codeTypeVote")
    libelle: str | None = Field(default=None, alias="libelleTypeVote")
    type_majorite: str | None = Field(default=None, alias="typeMajorite")


class Demandeur(CivixModel):
    """Auteur de la demande de scrutin."""

    texte: str | None = None


class ScrutinSummary(CivixModel):
    """Scrutin tel qu'il apparaît dans une liste."""

    uid: str
    legislature: int | None = None
    numero: int | None = None
    date_scrutin: datetime | None = None
    titre: str = ""
    objet: Objet | None = None
    sort: Sort | None = None
    type_vote: TypeVote | None = None
    context: str | None = None
    type: str | None = None
    sort_code: str | None = None
    tags: list[str] = Field(default_factory=list)

    @property
    def kind(self) -> str:
        """Nature du scrutin (amendement, article, texte ou autre), motions exclues du texte."""
        return classify_scrutin(self.type, self.titre)

    @property
    def dossier_ref(self) -> str | None:
        """Référence du dossier législatif, si elle existe."""
        dossier = self.objet.dossier_legislatif if self.objet else None
        return dossier.dossier_ref if dossier else None

    @property
    def dossier_libelle(self) -> str | None:
        """Titre du dossier législatif, s'il existe."""
        dossier = self.objet.dossier_legislatif if self.objet else None
        return dossier.libelle if dossier else None

    @property
    def adopted(self) -> bool | None:
        """Vrai si adopté, faux si rejeté, `None` si inconnu."""
        code = (self.sort_code or (self.sort.code if self.sort else None) or "").casefold()
        if code.startswith("adopt"):
            return True
        if code.startswith(("rejet", "non adopt")):
            return False
        return None


class ScrutinList(CivixModel):
    """Liste de scrutins (`/scrutins`)."""

    results: list[ScrutinSummary] = Field(default_factory=list)


class ScrutinDetail(CivixModel):
    """Détail d'un scrutin."""

    uid: str
    numero: int | None = None
    legislature: int | None = None
    date_scrutin: datetime | None = None
    titre: str = ""
    objet: Objet | None = None
    sort_code: str | None = None
    sort_libelle: str | None = None
    is_adopted: bool | None = None
    official_result: str | None = None
    majority_rule: str | None = None
    vote_mode: str | None = None
    type_vote: TypeVote | None = None
    demandeur: Demandeur | None = None
    tags: list[str] = Field(default_factory=list)

    @property
    def result_label(self) -> str | None:
        """Résultat officiel lisible."""
        return self.official_result or self.sort_libelle or self.sort_code


class VoteCounts(CivixModel):
    """Décompte des positions."""

    pour: int = 0
    contre: int = 0
    abstention: int = 0
    non_votant: int = 0
    unknown: int = 0
    total: int = 0


class GroupVoteCounts(VoteCounts):
    """Décompte des positions pour un groupe."""

    groupe_uid: str


class Scrutin(CivixModel):
    """Attributs de `/scrutins/{uid}` : détail et décomptes."""

    scrutin: ScrutinDetail
    results_global: VoteCounts | None = None
    results_by_group: list[GroupVoteCounts] = Field(default_factory=list)

    @field_validator("results_by_group", mode="before")
    @classmethod
    def drop_ungrouped(cls, rows: Any) -> Any:
        """Ignore les lignes sans groupe.

        Pour les 14e et 15e législatures, CIVIX ne ventile pas les votes par groupe et renvoie
        une seule ligne `groupe_uid: null` qui reprend le décompte global.
        """
        if not isinstance(rows, list):
            return rows
        return [row for row in rows if not isinstance(row, dict) or row.get("groupe_uid")]


class Vote(CivixModel):
    """Vote individuel d'un député."""

    deputy_uid: str
    prenom: str = ""
    nom: str = ""
    mandat_uid: str | None = None
    position: Position = Position.UNKNOWN
    par_delegation: bool | None = False
    """`None` quand CIVIX ne le précise pas (14e et 15e législatures)."""

    @property
    def full_name(self) -> str:
        """Prénom et nom."""
        return f"{self.prenom} {self.nom}".strip()


class ScrutinVotes(Scrutin):
    """Attributs de `/scrutins/{uid}/votes` : détail, décomptes et votes individuels."""

    votes: list[Vote] = Field(default_factory=list)


class GroupeStatement(CivixModel):
    """Déclaration publique d'un groupe sur un scrutin."""

    groupe_uid: str | None = None
    groupe_libelle: str | None = None
    groupe_abrev: str | None = None
    opinion_code: str | None = None
    public_reference: str | None = None
    vote_position: str | None = None
    statement: str = ""
    submitted_at: datetime | None = None
    status: str | None = None


class StatementList(CivixModel):
    """Déclarations publiques des groupes (`/scrutins/{uid}/statements`)."""

    statements: list[GroupeStatement] = Field(default_factory=list)
