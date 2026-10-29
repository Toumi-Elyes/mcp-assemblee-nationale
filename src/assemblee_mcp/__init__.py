"""Serveur MCP des votes de l'Assemblée nationale, bâti sur l'API ouverte CIVIX.

Où chercher, du réseau vers l'utilisateur :

- `civix/` : accès à CIVIX. `client` (appels, cache, nouvelles tentatives), `models/` (réponses
  en modèles Pydantic), `directory` (annuaire des députés), `lookup` et `search/` (recherches
  composées), `budget` (plafond d'appels par outil) et `errors` (messages d'erreur en français).
- `analytics/` : calculs purs sur les scrutins. `gather` collecte les données avec des volumes
  d'appels bornés, `stats/` calcule, `render/` met les résultats en markdown avec leur méthode,
  `exporting` produit le CSV et le JSON.
- `formatting/` : mise en forme markdown des réponses de consultation (scrutins, députés…).
- `tools/` : la couche MCP. Une classe par famille d'outils (`ToolSet`), `analyses/` pour les
  outils d'analyse, `common` pour les garde-fous (budget, délai, erreurs).
- `prompts.py`, `server.py`, `__main__.py` : prompts, assemblage du serveur et lancement.
- `limits.py` et `config.py` : tous les plafonds de charge et réglages, commentés.

Flux d'une demande : outil MCP → `civix.client` (cache, budget) → modèles Pydantic →
`analytics.stats` (calcul) → `analytics.render` ou `formatting` (texte) → réponse avec sources.
"""

__version__ = "0.1.0"
