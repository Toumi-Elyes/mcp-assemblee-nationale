"""Briques communes des modèles CIVIX : base Pydantic et position d'un vote."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


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
    def _missing_(cls, value: object) -> Position:
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
