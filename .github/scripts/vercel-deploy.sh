#!/usr/bin/env bash
# Déploie un projet Vercel depuis la racine du dépôt et écrit l'URL du déploiement sur stdout.
# Usage : vercel-deploy.sh <projet-vercel> <preview|production>
# Variables : VERCEL_TOKEN (secret), VERCEL_SCOPE (équipe), VERCEL_CLI (paquet npm épinglé).
set -euo pipefail

project="$1"
target="$2"
: "${VERCEL_TOKEN:?VERCEL_TOKEN manquant : ajoutez le secret du dépôt}"

vercel() {
  npx --yes "$VERCEL_CLI" "$@" --scope "$VERCEL_SCOPE" --token "$VERCEL_TOKEN"
}

vercel link --yes --project "$project" >&2
# `vercel link` télécharge les variables du projet (dont un jeton OIDC) dans .env.local :
# inutile ici, et à ne jamais envoyer avec les sources.
rm -f .env.local
if [ "$target" = production ]; then
  vercel deploy --yes --prod
else
  vercel deploy --yes
fi
