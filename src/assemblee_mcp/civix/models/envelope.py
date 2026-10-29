"""Enveloppe commune à toutes les réponses CIVIX : pagination, sources, citation."""

from pydantic import Field

from assemblee_mcp.civix.models.base import CivixModel
from assemblee_mcp.urls import safe_url

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
            if url.rstrip("/") != ASSEMBLEE_HOMEPAGE and (checked := safe_url(url)) is not None:
                return checked
        return None

    @property
    def civix_page(self) -> str | None:
        """Page CIVIX lisible par un humain."""
        return safe_url(self.civix_urls.get("page"))


class Citation(CivixModel):
    """Citation proposée par CIVIX."""

    text: str | None = None
    url: str | None = None


class Data[AttributesT: CivixModel](CivixModel):
    """Bloc `data` : type de ressource et attributs."""

    type: str | None = None
    attributes: AttributesT


class CivixResponse[AttributesT: CivixModel](CivixModel):
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
