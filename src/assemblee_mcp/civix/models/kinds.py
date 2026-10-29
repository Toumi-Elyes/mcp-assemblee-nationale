"""Classement d'un scrutin par nature : amendement, article, vote sur l'ensemble ou autre.

Le type publié par CIVIX est fiable pour les amendements et les articles, mais « texte » regroupe
aussi des motions (rejet préalable, censure…), des demandes de suspension de séance et des
prolongations de séance : seuls les votes sur l'ensemble d'un texte doivent compter comme tels.
"""

import re

KIND_AMENDEMENT = "amendement"
KIND_ARTICLE = "article"
KIND_ENSEMBLE = "texte"
KIND_AUTRE = "autre"

CIVIX_TYPE_TEXTE = "texte"
RELIABLE_CIVIX_TYPES = frozenset({KIND_AMENDEMENT, KIND_ARTICLE})
# Titres de motions et d'incidents de séance, jamais des votes sur l'ensemble d'un texte.
PROCEDURE_TITLE = re.compile(
    r"^(la |le |l['’])?(motion|question préalable|exception d['’]irrecevabilité"
    r"|demande (de|d['’])|proposition du gouvernement)"
)
# Titres des votes sur un texte pris dans son ensemble (première ou dernière lecture, etc.).
WHOLE_TEXT_TITLE = re.compile(r"^(l['’]ensemble|la proposition de loi|le projet de loi)")


def classify_scrutin(civix_type: str | None, title: str) -> str:
    """Nature d'un scrutin d'après son type CIVIX et son titre."""
    if civix_type in RELIABLE_CIVIX_TYPES:
        return civix_type
    folded = title.strip().casefold()
    if PROCEDURE_TITLE.match(folded):
        return KIND_AUTRE
    if civix_type == CIVIX_TYPE_TEXTE and WHOLE_TEXT_TITLE.match(folded):
        return KIND_ENSEMBLE
    return KIND_AUTRE
