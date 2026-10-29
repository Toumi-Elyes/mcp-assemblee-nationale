"""Recherche par mots-clés robuste : CIVIX cherche une sous-chaîne exacte.

« loi de finances 2027 » ne donne rien alors que « loi de finances pour 2027 » donne des
résultats. On essaie donc la requête telle quelle ; sans résultat, on interroge CIVIX avec le mot
le plus distinctif puis on filtre localement sur tous les autres mots, sans accents ni casse.
`broaden` prépare l'élargissement, `scrutins` cherche des scrutins, `everything` cherche partout.
"""

from assemblee_mcp.civix.search.broaden import broad_note, broaden, contains_all, summary_text
from assemblee_mcp.civix.search.everything import GlobalSearch, search_everything
from assemblee_mcp.civix.search.scrutins import (
    ScrutinPool,
    ScrutinSearch,
    search_scrutin_pool,
    search_scrutins,
)

__all__ = [
    "GlobalSearch",
    "ScrutinPool",
    "ScrutinSearch",
    "broad_note",
    "broaden",
    "contains_all",
    "search_everything",
    "search_scrutin_pool",
    "search_scrutins",
    "summary_text",
]
