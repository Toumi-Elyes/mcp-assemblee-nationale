"""Plafonds de charge : budgets d'appels, délais et tailles de pages.

Ces valeurs protègent l'API publique de CIVIX (« usage raisonnable ») et respectent la durée
maximale d'une fonction Vercel (60 s). Les modifier ici les change pour tout le serveur.
"""

# Appels réseau à CIVIX autorisés par appel d'outil (les réponses en cache ne comptent pas).
DEFAULT_MAX_CALLS = 10
# Outils qui lisent des pages de scrutins (une page = 50 scrutins, 20 pages au plus).
LISTING_MAX_CALLS = 30
# Outils qui lisent aussi le détail ou les votes de plusieurs dizaines de scrutins.
ANALYTICS_MAX_CALLS = 80

# « Comment a voté… ? » : résolution du député, recherche du sujet (jusqu'à 7 appels), 5 votes.
COMMENT_MAX_CALLS = 20

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
# Annuaire complet des députés (une quinzaine de pages) : lu au plus une fois par jour, hors
# budget d'appels, quand la recherche par nom de CIVIX ne suffit pas.
MAX_DIRECTORY_PAGES = 15
# CIVIX renvoie au plus 8 résultats par catégorie : au-delà, la liste est tronquée.
SEARCH_CATEGORY_CAP = 8
# Variantes d'un nom essayées dans la recherche CIVIX avant de lire l'annuaire.
MAX_NAME_SEARCHES = 4
# Scrutins maximum analysés en détail par les outils d'analyse (1 appel chacun, puis cache 24 h).
MAX_ANALYSED_SCRUTINS = 60
# Valeur par défaut : couvre un mois d'amendements sans épuiser le budget d'appels.
DEFAULT_ANALYSED_SCRUTINS = 40
# Les votes d'un député sont lus par lots jusqu'à ce que ce nombre de scrutins exploitables soit
# atteint (ou que l'échantillon soit épuisé) ; un lot reste proche de la limite de requêtes.
TARGET_USABLE_SCRUTINS = 25
VOTES_BATCH = 8
# En dessous de ce nombre de scrutins exploitables, une analyse prévient qu'elle est trop mince.
SMALL_SAMPLE_THRESHOLD = 10
# Recherche élargie par mots-clés : pages de 50 scrutins lues autour du mot le plus distinctif
# (les 300 plus récents). Requête exacte : pages lues pour la liste complète (les 100 plus récents).
BROAD_POOL_PAGES = 6
EXACT_POOL_PAGES = 2
# Durée maximale d'une période demandée, en jours.
MAX_RANGE_DAYS = 90
# Législature en cours, la seule bien couverte pour les députés.
CURRENT_LEGISLATURE = 17

# Cache partagé entre instances (Runtime Cache de Vercel) : changer ce numéro invalide toutes les
# entrées, à faire quand la forme d'un modèle CIVIX change.
SHARED_CACHE_SCHEMA_VERSION = 1
# Le Runtime Cache refuse un élément de plus de 2 Mo : au-delà, l'élément reste en mémoire seule.
SHARED_CACHE_MAX_BYTES = 2_000_000
# Un cache partagé lent ne doit jamais retarder une réponse : on lit CIVIX à la place.
SHARED_CACHE_TIMEOUT_SECONDS = 2.0
# Après un échec ou un délai dépassé, le cache partagé est ignoré pendant ce temps.
SHARED_CACHE_COOLDOWN_SECONDS = 60.0
# Accès simultanés au cache partagé (chaque accès ouvre sa propre connexion HTTP).
SHARED_CACHE_MAX_CONCURRENT = 8
