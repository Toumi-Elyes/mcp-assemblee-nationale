# 🏛️ MCP Assemblée nationale

**Demandez à Claude, ChatGPT ou Gemini comment ont voté les députés, en français, avec les sources.**

> « Comment a voté ma députée sur la réforme des retraites ? »
> « Quels groupes ont voté contre le dernier budget ? »
> « Résume-moi le scrutin sur l'aide à mourir, avec le détail par groupe. »

Ce projet branche votre assistant IA sur les **données publiques de l'Assemblée nationale**, via l'[API publique CIVIX](https://www.data.gouv.fr/dataservices/api-publique-civix) référencée sur data.gouv.fr. L'IA va chercher les vrais chiffres au lieu de répondre de mémoire, et elle cite le lien de chaque scrutin.

Gratuit, sans compte, sans clé, en lecture seule. Les données restent celles de l'Assemblée nationale : rien n'est interprété ni noté.

---

## Sommaire

- [Installer en 2 minutes (sans rien coder)](#-installer-en-2-minutes-sans-rien-coder)
  - [Claude](#claude-claudeai-et-application-claude)
  - [ChatGPT](#chatgpt)
  - [Gemini](#gemini)
  - [Claude Desktop, Cursor, autres (local)](#claude-desktop-cursor-et-autres-en-local)
- [Exemples de questions](#-exemples-de-questions)
- [Ce que l'IA peut faire](#-ce-que-lia-peut-faire)
- [D'où viennent les données](#-doù-viennent-les-données)
- [Questions fréquentes](#-questions-fréquentes)
- [Pour les développeurs](#-pour-les-développeurs)
- [English](#-english)

---

## ⚡ Installer en 2 minutes (sans rien coder)

Vous n'avez besoin que d'une adresse, à copier-coller dans votre assistant :

```
https://mcp-assemblee-nationale.fastmcp.app/mcp
```

### Claude (claude.ai et application Claude)

1. Ouvrez [claude.ai](https://claude.ai) et allez dans **Paramètres → Connecteurs**.
2. Cliquez sur **Ajouter un connecteur personnalisé**.
3. Nom : `Assemblée nationale`. URL : collez l'adresse ci-dessus.
4. Cliquez sur **Ajouter**. Aucune connexion n'est demandée.
5. Dans une nouvelle conversation, cliquez sur le bouton **+** (ou l'icône des outils) et vérifiez que **Assemblée nationale** est activé.

Le connecteur est ensuite disponible dans l'application Claude sur ordinateur et sur téléphone.

> Le plan gratuit de Claude autorise un connecteur personnalisé. Les plans payants en autorisent plusieurs. Sur un compte Team ou Enterprise, c'est l'administrateur qui l'ajoute pour l'organisation.

### ChatGPT

Les connecteurs personnalisés demandent un abonnement payant (Plus, Pro, Business, Enterprise ou Edu) et se configurent sur **chatgpt.com**, dans le navigateur.

1. Ouvrez **Paramètres → Applications et connecteurs → Paramètres avancés** et activez le **Mode développeur**.
   *Selon la version, ce réglage peut aussi se trouver dans **Paramètres → Sécurité**.*
2. Revenez dans **Applications et connecteurs** et cliquez sur **Créer**.
3. Nom : `Assemblée nationale`. URL du serveur MCP : collez l'adresse ci-dessus. Authentification : **Aucune**.
4. Cochez la case de confiance puis validez.
5. Dans une conversation, cliquez sur **+ → Mode développeur** et activez **Assemblée nationale**.

> ChatGPT affiche « non vérifié par OpenAI » pour toute application ajoutée soi-même : c'est normal. Ce serveur ne fait que lire des données publiques.

### Gemini

- **Application Gemini (gemini.google.com)** : à notre connaissance, elle ne permet pas encore d'ajouter son propre serveur MCP. Dès que ce sera possible, la même adresse fonctionnera.
- **Gemini CLI** (dans un terminal) : ajoutez ceci dans `~/.gemini/settings.json`, puis tapez `/mcp` dans Gemini CLI pour vérifier.

```json
{
  "mcpServers": {
    "assemblee-nationale": {
      "httpUrl": "https://mcp-assemblee-nationale.fastmcp.app/mcp"
    }
  }
}
```

### Claude Desktop, Cursor et autres (en local)

La méthode recommandée reste l'adresse ci-dessus : Claude Desktop reprend vos connecteurs claude.ai. Pour faire tourner le serveur sur votre ordinateur, installez [uv](https://docs.astral.sh/uv/getting-started/installation/) puis utilisez cette configuration :

```json
{
  "mcpServers": {
    "assemblee-nationale": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Toumi-Elyes/mcp-assemblee-nationale", "mcp-assemblee-nationale"]
    }
  }
}
```

- **Claude Desktop** : Paramètres → Développeur → Modifier la configuration, collez le bloc, redémarrez l'application.
- **Cursor** : `~/.cursor/mcp.json`.
- **Gemini CLI** : `~/.gemini/settings.json`.

---

## 💬 Exemples de questions

Posez vos questions normalement, en français :

- « Quels sont les derniers scrutins sur l'immigration ? »
- « Comment a voté [nom du député] sur la loi de finances ? »
- « Détaille le vote par groupe sur [sujet]. »
- « Quels députés du groupe Écologiste se sont abstenus sur ce scrutin ? »
- « Qu'ont déclaré les groupes avant le vote sur [sujet] ? »
- « Liste les groupes parlementaires et leur nombre de députés. »
- « Qui est le député de la 2e circonscription de l'Ariège ? »

Astuce : si l'IA ne trouve rien, reformulez avec un mot-clé du titre officiel (« retraites » plutôt que « la réforme de Borne »).

Le serveur propose aussi trois questions prêtes à l'emploi (menu des prompts dans Claude) : **Résumer un scrutin**, **Mon député**, **Comparer les groupes**.

---

## 🧰 Ce que l'IA peut faire

| Outil | À quoi il sert |
|---|---|
| `rechercher` | Chercher un député, un scrutin, un sujet |
| `rechercher_scrutins` | Trouver les scrutins sur un thème |
| `obtenir_scrutin` | Résultat d'un scrutin : adopté ou rejeté, pour, contre, abstentions, détail par groupe |
| `votes_scrutin` | Vote de chaque député, filtrable par groupe, position ou nom |
| `declarations_groupes` | Déclarations des groupes sur un scrutin |
| `comment_a_vote` | Comment un député a voté sur un sujet, en une question |
| `rechercher_deputes` / `obtenir_depute` | Trouver un député et sa fiche |
| `lister_groupes` / `obtenir_groupe` | Les groupes parlementaires |
| `search` / `fetch` | Les mêmes données au format attendu par la recherche approfondie de ChatGPT |

Tous les outils sont en lecture seule : l'IA ne peut rien modifier, ni nulle part.

---

## 📚 D'où viennent les données

- **Source** : les données ouvertes de l'[Assemblée nationale](https://data.assemblee-nationale.fr), mises à disposition par [CIVIX](https://www.civix.fr), une initiative indépendante, non officielle et neutre ([API sur data.gouv.fr](https://www.data.gouv.fr/dataservices/api-publique-civix)).
- **Licence des données** : Licence Ouverte Etalab 2.0.
- **Neutralité** : ce serveur transmet les chiffres tels quels. Il n'ajoute aucune analyse politique et chaque réponse renvoie vers la source.
- **Fraîcheur** : les réponses sont gardées en mémoire 10 minutes pour ménager l'API CIVIX. Un vote du jour peut mettre un peu de temps à apparaître, selon la mise à jour des données de l'Assemblée.

Ce projet n'est affilié ni à l'Assemblée nationale, ni à CIVIX.

---

## ❓ Questions fréquentes

**Est-ce gratuit ?** Oui. Le serveur, l'API CIVIX et l'hébergement sont gratuits. Seul l'abonnement à votre assistant (ChatGPT par exemple) peut être payant.

**Mes conversations sont-elles enregistrées ?** Le serveur ne reçoit que la recherche envoyée par l'IA (par exemple « retraites »), jamais votre conversation. Il ne garde aucun historique et n'utilise aucun cookie.

**L'IA dit qu'elle n'a pas accès à l'outil.** Vérifiez que le connecteur est activé dans la conversation (bouton **+**), puis demandez explicitement : « Utilise l'outil Assemblée nationale pour… ».

**L'IA s'est trompée.** Ouvrez le lien « Source » de la réponse : il mène à la page du scrutin. Si les données elles-mêmes semblent fausses, signalez-le à CIVIX. Si c'est le serveur, [ouvrez une issue](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/issues).

**Et le Sénat ?** Pas pour l'instant : l'API CIVIX couvre uniquement l'Assemblée nationale.

---

## 🛠️ Pour les développeurs

Serveur [MCP](https://modelcontextprotocol.io) en Python, construit avec [FastMCP](https://gofastmcp.com). Les réponses de l'API CIVIX sont validées par des modèles [Pydantic](https://docs.pydantic.dev), et les dépendances sont gérées avec [Poetry](https://python-poetry.org).

```
src/assemblee_mcp/
├── civix/
│   ├── client.py     client HTTP async (cache 10 min, délai max, nouvel essai)
│   ├── models.py     modèles Pydantic des réponses CIVIX
│   └── errors.py     erreurs lisibles pour l'utilisateur
├── tools/            outils MCP, regroupés par thème
├── formatting.py     mise en forme des réponses en français
├── prompts.py        questions prêtes à l'emploi
├── config.py         réglages (variables d'environnement)
├── server.py         assemble le serveur (`mcp`)
└── __main__.py       lancement en stdio ou en HTTP
```

### Lancer en local

Il faut Python 3.15 et Poetry 2.

```bash
poetry install
poetry run mcp-assemblee-nationale                    # stdio
poetry run mcp-assemblee-nationale --http --port 8000 # HTTP sur http://127.0.0.1:8000/mcp
npx @modelcontextprotocol/inspector poetry run mcp-assemblee-nationale  # tester les outils
```

### Vérifier

```bash
poetry run ruff check . && poetry run ruff format --check .
poetry run mypy src tests
poetry run pytest                          # tests hors ligne, sur des réponses CIVIX enregistrées
CIVIX_LIVE=1 poetry run pytest tests/live  # tests contre la vraie API CIVIX
```

### Réglages

| Variable | Défaut | Rôle |
|---|---|---|
| `CIVIX_BASE_URL` | `https://www.civix.fr/api/v1` | Adresse de l'API |
| `CIVIX_TIMEOUT` | `15` | Délai max d'un appel, en secondes |
| `CIVIX_CACHE_TTL` | `600` | Durée du cache, en secondes |

### Héberger votre propre copie

Le plus simple est [FastMCP Cloud](https://fastmcp.cloud), gratuit pour un projet personnel :

1. Forkez ce dépôt, puis connectez-vous à FastMCP Cloud avec GitHub.
2. Créez un projet à partir de votre fork, avec le point d'entrée `src/assemblee_mcp/server.py:mcp`.
3. Laissez l'authentification désactivée pour que Claude et ChatGPT puissent s'y connecter sans compte.

Chaque push sur `main` redéploie le serveur. Pour un autre hébergeur (Render, Fly.io, un VPS…), lancez `mcp-assemblee-nationale --http --host 0.0.0.0 --port $PORT`.

### Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md). Les issues et pull requests sont les bienvenues : nouvel outil, meilleure formulation des réponses, correction. Une règle : **des faits sourcés, aucune interprétation politique**.

---

## 🇬🇧 English

An [MCP](https://modelcontextprotocol.io) server that lets Claude, ChatGPT or Gemini answer questions about **French National Assembly votes** (scrutins, individual votes by deputy, parliamentary groups), using the open [CIVIX API](https://www.data.gouv.fr/dataservices/api-publique-civix). Free, no account, no API key, read-only, every answer links to its source.

- **Remote URL** (Claude custom connectors, ChatGPT developer mode, Gemini CLI `httpUrl`): `https://mcp-assemblee-nationale.fastmcp.app/mcp`
- **Local**: `uvx --from git+https://github.com/Toumi-Elyes/mcp-assemblee-nationale mcp-assemblee-nationale` (stdio)
- **Stack**: Python, FastMCP, Pydantic models, Poetry

Tool outputs are in French, since the underlying data is French.

## Licence

Code sous licence [MIT](LICENSE). Données : Licence Ouverte Etalab 2.0 (Assemblée nationale, via CIVIX).
