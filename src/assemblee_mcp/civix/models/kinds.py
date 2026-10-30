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


CIVIX_TYPE_AUTRE = "scrutin"
# « amende?ment » couvre aussi la coquille « sous-amendment » présente dans les archives.
AMENDEMENT_TITLE = re.compile(r"^(l['’]|les |le )?(sous-)?amende?ments?\b")
ARTICLE_TITLE = re.compile(r"^(l['’]|les )articles?\b")


def type_from_title(title: str) -> str:
    """Type CIVIX déduit du titre, pour les scrutins que CIVIX publie sans type (14e et 15e).

    Reprend le découpage de CIVIX : `amendement` (sous-amendements compris), `article`, `texte`
    (votes sur l'ensemble et motions, que `classify_scrutin` sépare ensuite) et `scrutin`.
    """
    folded = title.strip().casefold()
    if AMENDEMENT_TITLE.match(folded):
        return KIND_AMENDEMENT
    if ARTICLE_TITLE.match(folded):
        return KIND_ARTICLE
    if WHOLE_TEXT_TITLE.match(folded) or PROCEDURE_TITLE.match(folded):
        return CIVIX_TYPE_TEXTE
    return CIVIX_TYPE_AUTRE
