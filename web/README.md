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

## Stratégie de cache

| Couche | Où | Durée | Détail |
|---|---|---|---|
| Cache de données Next, par appel CIVIX | `next: { revalidate }` dans `src/lib/civix/client.ts` | 10 min (recherche), 30 min (listes de scrutins), 6 h (détail, votes, déclarations), 24 h (groupes, députés) | Une même adresse CIVIX n'est appelée qu'une fois par durée, quel que soit le nombre de pages qui la demandent. |
| Pages ISR | `/` | 1800 s | Régénérée en arrière plan. Si CIVIX ne répond pas pendant la régénération, la page lève une erreur et la dernière version valide reste servie. Le repli « Données momentanément indisponibles » n'existe qu'au build. |
| | `/scrutins/[uid]` | 21600 s | `generateStaticParams` préconstruit les 50 derniers scrutins, `dynamicParams` accepte les autres à la demande. Un identifiant bien formé mais inconnu donne un 404 mis en cache par ISR. Un identifiant mal formé est rejeté sans appel. |
| CDN, en têtes `s-maxage` | `/api/live` | 120 s + `stale-while-revalidate` 600 s | Chiffres du hero et liste de la semaine. |
| | `/api/deputes`, `/api/demo` | 600 s + `stale-while-revalidate` 3600 s | Réponses 200. Les 400 et 404 sont mises en cache 300 s, les 403 et 502 jamais. |
| Client | `LiveProvider` | toutes les 3 minutes | Seulement onglet visible, en ligne et sans demande de réduction de données. Pause quand l'onglet est caché, une relecture dès le retour si les données ont plus de 3 minutes. Reprise exponentielle après erreur, plafonnée à 15 minutes. Annulation de la requête en cours au démontage. |

La limitation de débit est faite au pare feu de l'hébergeur (60 requêtes par minute et par IP sur `/api/*` et `/scrutins/*`), pas dans ce code.

## Déploiement sur Vercel

1. Importer le dépôt dans un nouveau projet Vercel.
2. Dans **Settings, General, Root Directory**, choisir `web`. Framework : Next.js (détecté).
3. Définir `NEXT_PUBLIC_MCP_URL` si l'adresse du connecteur diffère de la valeur par défaut.
4. Déployer. Aucune base de données, aucun secret.
