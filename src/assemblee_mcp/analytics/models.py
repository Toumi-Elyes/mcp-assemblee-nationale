"""Modèles Pydantic des résultats d'analyses (agrégats calculés à partir des données CIVIX)."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ResultModel(BaseModel):
    """Base des résultats : immuables, sans champ inattendu."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Stance(StrEnum):
    """Position majoritaire d'un groupe sur un scrutin."""

    POUR = "pour"
    CONTRE = "contre"
    ABSTENTION = "abstention"
    PARTAGE = "partagé"


class Method(ResultModel):
    """Informations de méthode affichées sous chaque analyse."""

    period: str | None = None
    analysed: int
    matching: int | None = None
    counted: str
    limits: list[str] = Field(default_factory=list)
    truncated: bool = False
    notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    legislature: int | None = None


class Rate(ResultModel):
    """Effectif et part de scrutins adoptés pour une catégorie."""

    label: str
    total: int
    adopted: int
    rejected: int

    @property
    def rate(self) -> float | None:
        """Part de scrutins adoptés parmi ceux dont le sort est connu."""
        decided = self.adopted + self.rejected
        return self.adopted / decided if decided else None


class WeekVolume(ResultModel):
    """Nombre de scrutins sur une semaine (du lundi au dimanche)."""

    week_start: date
    scrutins: int
    adopted: int


class DayVolume(ResultModel):
    """Nombre de scrutins un jour donné."""

    day: date
    scrutins: int


class Trends(ResultModel):
    """Tendances générales sur une période."""

    start: date
    end: date
    total: int
    overall: Rate
    weeks: list[WeekVolume]
    by_type: list[Rate]
    by_context: list[Rate]
    busiest_days: list[DayVolume]


class TextActivity(ResultModel):
    """Activité de vote sur un dossier législatif."""

    dossier_ref: str | None
    libelle: str
    context: str | None
    scrutins: int
    adopted: int
    rejected: int
    amendements: int
    articles: int
    ensemble: int
    last_date: date | None


class TimelineEntry(ResultModel):
    """Scrutin d'un dossier dans la chronologie."""

    uid: str
    legislature: int | None = None
    numero: int | None
    day: date | None
    kind: str
    result: str
    title: str


class DossierTimeline(ResultModel):
    """Chronologie des scrutins d'un dossier législatif."""

    dossier_ref: str | None
    libelle: str
    context: str | None
    total: int
    amendements: Rate
    entries: list[TimelineEntry]
    final_votes: list[TimelineEntry]
    other_dossiers: list[TextActivity]


class ScrutinRef(ResultModel):
    """Référence courte d'un scrutin analysé."""

    uid: str
    numero: int | None
    day: date | None
    title: str
    result: str


class GroupStances(ResultModel):
    """Position majoritaire de chaque groupe sur un scrutin."""

    scrutin: ScrutinRef
    stances: dict[str, Stance | None]


class PairAgreement(ResultModel):
    """Accord entre deux groupes sur les scrutins où ils ont tous deux une position."""

    group_a: str
    group_b: str
    shared: int
    agreed: int

    @property
    def rate(self) -> float | None:
        """Part de scrutins où les deux groupes ont la même position majoritaire."""
        return self.agreed / self.shared if self.shared else None


class GroupCohesion(ResultModel):
    """Part des votes exprimés d'un groupe alignés sur sa position majoritaire."""

    group: str
    scrutins: int
    expressed: int
    aligned: int

    @property
    def rate(self) -> float | None:
        """Part des votes exprimés conformes à la position majoritaire du groupe."""
        return self.aligned / self.expressed if self.expressed else None


class CloseVote(ResultModel):
    """Scrutin au résultat serré."""

    scrutin: ScrutinRef
    pour: int
    contre: int
    abstention: int

    @property
    def margin(self) -> int:
        """Écart entre les voix pour et contre."""
        return abs(self.pour - self.contre)


class DeputeBilan(ResultModel):
    """Distribution des positions d'un député sur un échantillon de scrutins."""

    name: str
    group: str | None
    scrutins: int
    pour: int
    contre: int
    abstention: int
    non_votant: int
    absent: int
    by_delegation: int
    comparable: int
    aligned: int

    @property
    def alignment_rate(self) -> float | None:
        """Part des votes exprimés conformes à la position majoritaire du groupe."""
        return self.aligned / self.comparable if self.comparable else None


class DeputeComparison(ResultModel):
    """Accord entre deux députés sur les scrutins où tous deux ont exprimé un vote."""

    name_a: str
    name_b: str
    scrutins: int
    shared: int
    agreed: int
    only_a: int
    only_b: int

    @property
    def rate(self) -> float | None:
        """Part de scrutins communs où les deux députés ont voté de la même façon."""
        return self.agreed / self.shared if self.shared else None


class GroupSeats(ResultModel):
    """Effectif d'un groupe parlementaire."""

    abbr: str
    libelle: str
    effectif: int | None


class AssemblyStats(ResultModel):
    """Chiffres d'ensemble de la législature."""

    legislature: int | None
    total_scrutins: int | None
    sample_size: int
    overall: Rate
    by_type: list[Rate]
    groups: list[GroupSeats]
    deputies: int | None
