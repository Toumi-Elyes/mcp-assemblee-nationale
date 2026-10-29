"""Modèles Pydantic des réponses de l'API CIVIX.

Seul le bloc `data.attributes` de chaque réponse est modélisé : CIVIX en recopie le contenu
directement sous `data`, ce que `extra="ignore"` écarte.
"""

from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class CivixModel(BaseModel):
    """Base commune : champs inconnus ignorés, modèles immuables."""

    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)


class Position(StrEnum):
    """Position prise par un député lors d'un scrutin."""

    POUR = "pour"
    CONTRE = "contre"
    ABSTENTION = "abstention"
    NON_VOTANT = "non_votant"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "Position":
        return cls.UNKNOWN

    @property
    def label(self) -> str:
        """Libellé français de la position."""
        return POSITION_LABELS[self]


POSITION_LABELS: dict[Position, str] = {
    Position.POUR: "Pour",
    Position.CONTRE: "Contre",
    Position.ABSTENTION: "Abstention",
    Position.NON_VOTANT: "Non-votant",
    Position.UNKNOWN: "Position inconnue",
}

ASSEMBLEE_HOMEPAGE = "https://www.assemblee-nationale.fr"


class Pagination(CivixModel):
    """Pagination d'une liste ; les champs varient selon le point d'accès."""

    page: int | None = None
    page_size: int | None = None
    next_page: int | None = None
    count_total: int | None = None
    count_estimated: int | None = None
    count_returned: int | None = None

    @property
    def total(self) -> int | None:
        """Nombre total de résultats, exact ou estimé."""
        return self.count_total if self.count_total is not None else self.count_estimated


class Meta(CivixModel):
    """Métadonnées de la réponse."""

    pagination: Pagination | None = None


class Source(CivixModel):
    """Sources de la donnée."""

    source_urls: list[str] = Field(default_factory=list)
    civix_urls: dict[str, str] = Field(default_factory=dict)

    @property
    def assemblee_url(self) -> str | None:
        """Lien précis vers l'Assemblée nationale, hors simple page d'accueil."""
        for url in self.source_urls:
            if url.rstrip("/") != ASSEMBLEE_HOMEPAGE:
                return url
        return None

    @property
    def civix_page(self) -> str | None:
        """Page CIVIX lisible par un humain."""
        return self.civix_urls.get("page")


class Citation(CivixModel):
    """Citation proposée par CIVIX."""

    text: str | None = None
    url: str | None = None


AttributesT = TypeVar("AttributesT", bound=CivixModel)


class Data(CivixModel, Generic[AttributesT]):
    """Bloc `data` : type de ressource et attributs."""

    type: str | None = None
    attributes: AttributesT


class CivixResponse(CivixModel, Generic[AttributesT]):
    """Enveloppe commune à toutes les réponses CIVIX."""

    answer: str | None = None
    summary: str | None = None
    canonical_url: str | None = None
    meta: Meta = Field(default_factory=Meta)
    source: Source = Field(default_factory=Source)
    citation: Citation | None = None
    data: Data[AttributesT]

    @property
    def attributes(self) -> AttributesT:
        """Raccourci vers `data.attributes`."""
        return self.data.attributes

    @property
    def pagination(self) -> Pagination | None:
        """Raccourci vers `meta.pagination`."""
        return self.meta.pagination


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
    tags: list[str] = Field(default_factory=list)


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


class Vote(CivixModel):
    """Vote individuel d'un député."""

    deputy_uid: str
    prenom: str = ""
    nom: str = ""
    mandat_uid: str | None = None
    position: Position = Position.UNKNOWN
    par_delegation: bool = False

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


class DeputeUrls(CivixModel):
    """Liens d'un député."""

    civix_page: str | None = None
    civix_api: str | None = None
    assemblee: str | None = None


class Depute(CivixModel):
    """Un député."""

    uid: str
    prenom: str = ""
    nom: str = ""
    legislature: int | None = None
    circ_num: int | None = None
    circ_departement: str | None = None
    groupe_uid: str | None = None
    groupe_abrev: str | None = None
    groupe_libelle: str | None = None
    urls: DeputeUrls | None = None

    @property
    def full_name(self) -> str:
        """Prénom et nom."""
        return f"{self.prenom} {self.nom}".strip()


class DeputeList(CivixModel):
    """Liste de députés (`/deputes`)."""

    results: list[Depute] = Field(default_factory=list)


class DeputeDetail(CivixModel):
    """Attributs de `/deputes/{uid}`."""

    deputy: Depute


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


SearchResponse = CivixResponse[SearchResults]
ScrutinListResponse = CivixResponse[ScrutinList]
ScrutinResponse = CivixResponse[Scrutin]
ScrutinVotesResponse = CivixResponse[ScrutinVotes]
StatementsResponse = CivixResponse[StatementList]
DeputeListResponse = CivixResponse[DeputeList]
DeputeDetailResponse = CivixResponse[DeputeDetail]
GroupeListResponse = CivixResponse[GroupeList]
GroupeDetailResponse = CivixResponse[GroupeDetail]
