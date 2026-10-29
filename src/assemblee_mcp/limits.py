"""Plafonds de charge : budgets d'appels, délais et tailles de pages.

Ces valeurs protègent l'API publique de CIVIX (« usage raisonnable ») et respectent la durée
maximale d'une fonction Vercel (60 s). Les modifier ici les change pour tout le serveur.
"""

# Appels réseau à CIVIX autorisés par appel d'outil (les réponses en cache ne comptent pas).
DEFAULT_MAX_CALLS = 10
# Recherche de députés : parcourir tout l'annuaire (une quinzaine de pages) est un dernier recours.
DIRECTORY_MAX_CALLS = 20
# Outils qui lisent des pages de scrutins (une page = 50 scrutins, 20 pages au plus).
LISTING_MAX_CALLS = 30
# Outils qui lisent aussi le détail ou les votes de plusieurs dizaines de scrutins.
ANALYTICS_MAX_CALLS = 45

# Durée maximale d'un outil, en secondes ; une fonction Vercel s'arrête à 60 s.
TOOL_DEADLINE_SECONDS = 25.0
ANALYTICS_DEADLINE_SECONDS = 45.0

# Éléments par page dans les réponses des outils de consultation.
DEFAULT_PAGE_SIZE = 10
# Éléments par page dans les listes d'analyses filtrées localement.
LOCAL_PAGE_SIZE = 20
# Taille de page maximale acceptée par CIVIX.
CIVIX_PAGE_SIZE = 50
# Pages de scrutins lues au plus pour une période (CIVIX_PAGE_SIZE scrutins par page).
MAX_LIST_PAGES = 20
# Pages lues en parallèle ; reste proche de la limite de requêtes simultanées du client.
BATCH_PAGES = 3
# Pages lues pour constituer un échantillon de scrutins à analyser en détail.
SAMPLE_MAX_PAGES = 10
# Pages de scrutins d'un dossier législatif lues au plus (chronologie).
DOSSIER_MAX_PAGES = 6
# Pages réparties sur la législature pour estimer des parts d'adoption.
LEGISLATURE_SAMPLE_PAGES = 10
# Durée maximale d'une période demandée, en jours.
MAX_RANGE_DAYS = 90
# Législature en cours, la seule bien couverte pour les députés.
CURRENT_LEGISLATURE = 17
