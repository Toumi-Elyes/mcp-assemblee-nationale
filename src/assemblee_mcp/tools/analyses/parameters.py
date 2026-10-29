"""Paramètres communs aux outils d'analyse : types validés et critères de sélection."""

from typing import Annotated, Literal

from fastmcp.exceptions import ToolError
from pydantic import Field

KindName = Literal["tous", "texte", "article", "amendement", "autre"]
# Traduction des noms proposés au modèle vers les types publiés par CIVIX (`None` = tous).
KIND_VALUES: dict[str, str | None] = {
    "tous": None,
    "texte": "texte",
    "article": "article",
    "amendement": "amendement",
    "autre": "scrutin",
}
KIND_DESCRIPTION = (
    "Type de scrutin : `texte` (vote sur l'ensemble d'un texte), `article`, `amendement`, "
    "`autre` (motions…) ou `tous`."
)

PeriodDays = Annotated[
    int, Field(description="Nombre de jours à analyser, jusqu'à aujourd'hui.", ge=7, le=90)
]
SamplePeriodDays = Annotated[
    int,
    Field(
        description="Nombre de jours à analyser, jusqu'à aujourd'hui (30 au plus).",
        ge=7,
        le=30,
    ),
]
OptionalSamplePeriodDays = Annotated[
    SamplePeriodDays | None, Field(description="Jours à analyser.")
]
MaxScrutins = Annotated[
    int,
    Field(
        description="Nombre maximal de scrutins analysés (échantillon borné).",
        ge=3,
        le=30,
    ),
]
OptionalSubject = Annotated[
    str | None,
    Field(description="Sujet en mots-clés (« retraites »), avec accents.", max_length=200),
]
DossierReference = Annotated[
    str,
    Field(
        description="Référence d'un dossier législatif, par exemple « DLR5L17N54898 ».",
        pattern=r"^DLR[A-Za-z0-9]{3,30}$",
    ),
]
KindParameter = Annotated[KindName, Field(description=KIND_DESCRIPTION)]


def require_subject_or_dossier(subject: str | None, dossier: str | None) -> str:
    """Requête issue de `sujet` ou `dossier` (un seul des deux)."""
    if (subject is None) == (dossier is None):
        raise ToolError("Indiquez soit `sujet`, soit `dossier` (un seul des deux).")
    return subject if subject is not None else str(dossier)


def require_subject_or_period(subject: str | None, days: int | None) -> None:
    """Vérifie qu'un seul critère de sélection (`sujet` ou `periode_jours`) est donné."""
    if (subject is None) == (days is None):
        raise ToolError("Indiquez soit `sujet`, soit `periode_jours` (un seul des deux).")
