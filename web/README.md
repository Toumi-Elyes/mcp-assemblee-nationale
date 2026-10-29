# Site web du projet

Page d'accueil publique du connecteur MCP Assemblée nationale : explication, installation, données en direct et démonstration. Next.js 16 (App Router), React 19, TypeScript strict, Tailwind CSS 4, icônes Phosphor, polices Public Sans et Spectral (auto hébergées).

## Commandes

```bash
pnpm install
pnpm dev          # http://localhost:3000
pnpm lint
pnpm exec tsc --noEmit
pnpm test
pnpm build && pnpm start
```

Le système de conception suivi est décrit dans `DESIGN.md` (plan, copie, FAQ, SEO, checklist).

## Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `NEXT_PUBLIC_MCP_URL` | `https://mcp-assemblee-nationale.vercel.app/mcp` | Adresse du connecteur affichée et copiée |
| `NEXT_PUBLIC_SITE_URL` | `VERCEL_PROJECT_PRODUCTION_URL`, sinon `http://localhost:3000` | URL canonique, sitemap, image de partage |
| `CIVIX_BASE_URL` | `https://www.civix.fr/api/v1` | API CIVIX lue côté serveur |

Si CIVIX ne répond pas, le build réussit et les blocs de données affichent « Données momentanément indisponibles ».

## Données en direct

Toutes les données viennent de CIVIX, jamais de valeurs écrites à la main. L'accueil est régénéré toutes les 30 minutes (`revalidate = 1800`), les pages `/scrutins/[uid]` toutes les 6 heures, la démo et l'autocomplétion passent par `/api/demo` et `/api/deputes` (cache 10 minutes).

Appels CIVIX par régénération de l'accueil, au pire : jusqu'à 10 pages de scrutins, 1 total de législature, 1 liste des groupes, 1 recherche des votes sur l'ensemble, jusqu'à 5 vérifications de sujets, 1 liste de votes (députés présents), 1 page de députés, jusqu'à 15 détails de scrutins. L'exemple du hero réutilise des appels déjà faits. La page d'un scrutin charge le vote, les groupes, les déclarations, puis l'annuaire complet des députés (environ 12 pages) pour afficher le groupe de chacun.

## Déploiement sur Vercel

1. Importer le dépôt dans un nouveau projet Vercel.
2. Dans **Settings, General, Root Directory**, choisir `web`. Framework : Next.js (détecté).
3. Définir `NEXT_PUBLIC_MCP_URL` si l'adresse du connecteur diffère de la valeur par défaut.
4. Déployer. Aucune base de données, aucun secret.
