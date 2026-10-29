# Site vitrine MCP Assemblée nationale

Application Next.js (App Router, Tailwind CSS v4, TypeScript strict) qui affiche en direct des données réelles de l'API [CIVIX](https://www.civix.fr) et présente le serveur MCP. Aucune donnée n'est écrite en dur : tout vient de CIVIX, côté serveur, avec cache de 30 minutes.

## Commandes

```bash
pnpm install
pnpm dev          # http://localhost:3000
pnpm lint
pnpm exec tsc --noEmit
pnpm test         # vitest, fixtures dans test/fixtures
pnpm build && pnpm start
```

## Variables d'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `NEXT_PUBLIC_MCP_URL` | Adresse du serveur MCP affichée et copiable | `https://mcp-assemblee-nationale.vercel.app/mcp` |
| `NEXT_PUBLIC_SITE_URL` | URL publique (sitemap, Open Graph) | URL de production Vercel, sinon `http://localhost:3000` |
| `CIVIX_BASE_URL` | Base de l'API CIVIX | `https://www.civix.fr/api/v1` |

Si CIVIX est indisponible, le build et les pages réussissent : chaque section affiche « Données momentanément indisponibles ».

## Déploiement sur Vercel

1. Importer le dépôt dans Vercel.
2. Régler **Root Directory** sur `web`.
3. Framework : Next.js (détecté). Commandes par défaut (pnpm est détecté via `pnpm-lock.yaml`).
4. Renseigner `NEXT_PUBLIC_MCP_URL` et `NEXT_PUBLIC_SITE_URL`.

## Structure

- `src/lib/civix/` : client typé (zod), serveur uniquement, timeout 15 s.
- `src/lib/stats/` : fonctions pures de tendances, testées.
- `src/lib/data/` : assemblage des données par page, avec repli en cas d'erreur.
- `src/app/api/` : routes de la démo (`/api/deputes`, `/api/demo`).
