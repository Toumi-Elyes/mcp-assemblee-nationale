# Code source de `assemblee_mcp`

Serveur MCP qui répond aux questions sur les votes de l'Assemblée nationale à partir de l'API
ouverte CIVIX. Ce guide dit où chercher ; le détail est dans la docstring de chaque module.

## Flux d'une demande

```
outil MCP (tools/)
  → client CIVIX (civix/client.py : cache L1 mémoire puis L2 partagé, budget d'appels, nouvelle tentative)
  → modèles Pydantic (civix/models/)
  → calcul pur (analytics/stats/)            pour les analyses
  → texte markdown (analytics/render/ ou formatting/)
  → réponse avec bloc « Méthode », lien source et pied de page
```

## Les paquets

| Chemin | Rôle |
|---|---|
| `civix/` | Tout ce qui parle à CIVIX : `client`, `cache` (L1, mémoire), `shared_cache` (L2, Runtime Cache de Vercel : voir README racine, « Caches »), `directory` (annuaire des députés gardé 24 h, hors budget), `models/` (une réponse = un modèle ; `kinds` classe amendement / article / texte / autre), `lookup` (résolveur unique de députés, groupes, pour toutes les législatures couvertes), `archive` (députés, groupes et appartenances datées des 14e à 16e législatures, lus dans `data/`), `search/` (recherche par mots-clés robuste, requête élargie), `budget`, `errors`. |
| `data/` | Index des législatures closes (`legislature_<n>.json`), produits par `scripts/build_legislature_data.py` à partir de l'archive AMO30 historique de l'Assemblée nationale. |
| `analytics/` | Analyses sur plusieurs scrutins. `gather` lit les données avec des volumes bornés, `stats/` calcule (fonctions pures, testées sans réseau), `render/` met en forme, `exporting` produit CSV et JSON. |
| `formatting/` | Mise en forme des réponses de consultation : scrutins, votes, déclarations, députés, groupes, recherche. Nettoie aussi les textes tiers (`text`). |
| `tools/` | La couche MCP. Une classe par famille d'outils (`ToolSet`) : chaque outil est une méthode, le client CIVIX est un attribut. `tools/analyses/` regroupe les outils d'analyse. |
| `limits.py`, `config.py` | Tous les plafonds de charge (budgets d'appels, délais, tailles de pages) et réglages, avec leur raison. |
| `server.py`, `prompts.py`, `__main__.py` | Assemblage du serveur, prompts, lancement (stdio ou HTTP). |

## Ajouter un outil

1. Si c'est un calcul, écrire une fonction pure dans `analytics/stats/` et son rendu dans
   `analytics/render/`, avec des tests sur de petites données fabriquées.
2. Ajouter une méthode asynchrone à la classe de la famille concernée dans `tools/`, décorée
   par `civix_tool` (ou `limited(...)` pour un budget d'appels plus grand), avec une docstring
   en français pensée pour qu'un modèle choisisse le bon outil.
3. La déclarer dans `tools()` de la classe ; l'enregistrement et les annotations « lecture
   seule » sont faits par `ToolSet.register`.

## Règles

- Neutralité : des faits et des chiffres, jamais d'interprétation politique ni de classement
  de personnes. Chaque analyse annonce sa méthode et la taille de son échantillon.
- Les contenus venant de CIVIX sont tiers : ils passent par `formatting.text` (nettoyage,
  plafonds) et les liens par `urls.safe_url`.
