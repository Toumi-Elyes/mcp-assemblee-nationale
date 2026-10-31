# Contribuer

Merci de votre aide ! Ce projet est un serveur MCP en Python qui rend les votes de l'Assemblée nationale accessibles à Claude, ChatGPT ou Gemini via l'API publique [CIVIX](https://www.civix.fr/api).

## Installation

Prérequis : Python 3.14 ou plus récent (développement en 3.15) et [Poetry](https://python-poetry.org/).

```bash
poetry install
```

## Commandes

```bash
poetry run ruff check .            # lint
poetry run ruff format .           # formatage
poetry run mypy src tests api      # typage strict
poetry run pytest                  # tests (API simulée, sans réseau)
CIVIX_LIVE=1 poetry run pytest tests/live   # tests contre l'API réelle
poetry run mcp-assemblee-nationale          # serveur stdio
poetry run mcp-assemblee-nationale --http --port 8765   # HTTP sur /mcp
```

Avant d'ouvrir une pull request, `ruff check`, `ruff format --check`, `mypy` et `pytest` doivent passer (c'est ce que fait la CI).

## Proposer un changement

La branche `main` est protégée : on ne pousse pas dessus directement.

1. Forkez le dépôt (ou créez une branche si vous avez les droits), puis travaillez sur une branche dédiée.
2. Ouvrez une pull request vers `main`.
3. La CI doit être verte (lint, format, typage, tests) avant la fusion.
4. Si la PR change ce que le connecteur sait faire ou ce que voit le visiteur de la landing (nouvel outil, amélioration visible, correction), ajoutez une entrée datée au journal des nouveautés dans `web/src/content/changelog.ts`, puis lancez `pnpm changelog` dans `web/` pour régénérer [CHANGELOG.md](CHANGELOG.md). La landing l'affiche dans sa section « Nouveautés » et sur `/nouveautes` ; un test vérifie que les deux restent identiques.

Une faille de sécurité ne s'ouvre pas en issue : voir [SECURITY.md](SECURITY.md).

## Règles de code

- Typage complet, pas de `Any` hors de la frontière JSON brute.
- Les réponses de CIVIX sont lues par des modèles Pydantic (`src/assemblee_mcp/civix/models/`) ; la mise en forme est dans `formatting/` et `analytics/render/`, sans appel réseau. Le plan du code est dans `src/assemblee_mcp/README.md`.
- Un nouvel outil : un module dans `src/assemblee_mcp/tools/`, une description en français rédigée pour qu'un modèle choisisse le bon outil, les annotations en lecture seule, et des tests avec les fixtures de `tests/fixtures/`.
- Tout scrutin cité dans une réponse porte son lien exact (`links.scrutin_page_url`) : un assistant qui doit deviner une adresse tombe souvent sur une page d'erreur. `tests/test_links.py` le vérifie.
- Les skills Claude Code personnels restent dans `~/.claude/skills` : `.claude/skills/` est ignoré par git. La charte du site est `web/DESIGN.md`.

## Règle de neutralité

Le serveur restitue des données publiques, sans opinion. Les sorties ne doivent contenir aucune interprétation politique, aucun jugement sur un député ou un groupe, aucun qualificatif partisan : uniquement des faits (positions, décomptes, résultats officiels), toujours accompagnés du lien source. Toute contribution qui ajoute de l'analyse, du classement ou de l'éditorial sera refusée.

## Issues et pull requests

Pour signaler un bug, une donnée incorrecte ou proposer une amélioration, utilisez les formulaires proposés à l'ouverture d'une issue : ils ajoutent l'issue au [tableau du projet](https://github.com/users/Toumi-Elyes/projects/3) avec le bon label. Les failles de sécurité se signalent en privé (voir [SECURITY.md](SECURITY.md)).

Dans une pull request, indiquez `Closes #<numéro>` : la carte du tableau passe alors en « In Review » à l'ouverture et en « Done » à la fusion.

## Déploiement

Les déploiements passent par GitHub Actions (`.github/workflows/deploy.yml`), pas par l'intégration Git de Vercel, coupée dans `vercel.json` et `web/vercel.json` : elle redéployait les deux projets à chaque push de PR et épuisait le quota du plan Hobby (100 déploiements par jour).

- **Production** : automatique après la fusion sur `main`, une fois la CI verte. Le serveur MCP est redéployé à la fin du workflow « CI », la landing à la fin du workflow « Web » (qui ne tourne que si `web/` change). Si un commit plus récent est déjà sur `main`, c'est lui qui est déployé.
- **Prévisualisation d'une PR** : posez le label `preview` sur la PR. Seuls les projets touchés par la PR sont déployés, et les adresses sont publiées en commentaire. Pour redéployer après de nouveaux commits, retirez puis remettez le label.
- **À la demande** : onglet **Actions → Déploiement → Run workflow**, en choisissant le projet (connecteur, landing ou les deux), l'environnement et la branche. La production n'est possible que depuis `main`.

Le workflow utilise le secret `VERCEL_TOKEN` (jeton Vercel limité à l'équipe `mcp-assemblee-nationale`) et la CLI Vercel épinglée dans `VERCEL_CLI`.
