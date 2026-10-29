# Contribuer

Merci de votre aide ! Ce projet est un serveur MCP en Python qui rend les votes de l'Assemblée nationale accessibles à Claude, ChatGPT ou Gemini via l'API publique [CIVIX](https://www.civix.fr/api).

## Installation

Prérequis : Python 3.15 et [Poetry](https://python-poetry.org/).

```bash
poetry install
```

## Commandes

```bash
poetry run ruff check .            # lint
poetry run ruff format .           # formatage
poetry run mypy src tests          # typage strict
poetry run pytest                  # tests (API simulée, sans réseau)
CIVIX_LIVE=1 poetry run pytest tests/live   # tests contre l'API réelle
poetry run mcp-assemblee-nationale          # serveur stdio
poetry run mcp-assemblee-nationale --http --port 8765   # HTTP sur /mcp
```

Avant d'ouvrir une pull request, `ruff check`, `ruff format --check`, `mypy` et `pytest` doivent passer (c'est ce que fait la CI).

## Règles de code

- Typage complet, pas de `Any` hors de la frontière JSON brute.
- Les réponses de CIVIX sont lues par des modèles Pydantic (`src/assemblee_mcp/civix/models.py`) ; la mise en forme est dans `formatting.py`, sans appel réseau.
- Un nouvel outil : un module dans `src/assemblee_mcp/tools/`, une description en français rédigée pour qu'un modèle choisisse le bon outil, les annotations en lecture seule, et des tests avec les fixtures de `tests/fixtures/`.

## Règle de neutralité

Le serveur restitue des données publiques, sans opinion. Les sorties ne doivent contenir aucune interprétation politique, aucun jugement sur un député ou un groupe, aucun qualificatif partisan : uniquement des faits (positions, décomptes, résultats officiels), toujours accompagnés du lien source. Toute contribution qui ajoute de l'analyse, du classement ou de l'éditorial sera refusée.
