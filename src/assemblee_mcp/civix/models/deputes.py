"""Modèles des députés."""

from pydantic import Field

from assemblee_mcp.civix.models.base import CivixModel


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
