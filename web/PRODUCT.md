# Product

<!-- impeccable:product-schema 1 -->

> Written by a delegated agent from the owner's brief and the repository (README.md, DESIGN.md history, source). No live interview took place; facts below are taken from the brief and code. Items marked *(inferred)* were not confirmed by the owner.

## Platform

web

## Users

French residents without a technical background who use a general AI assistant (Claude, ChatGPT, Gemini) and want to know how the Assemblée nationale voted: on a text, a subject, or for one deputy. Secondary audiences: journalists, teachers, students, civic associations *(inferred from DESIGN.md hypotheses)*. Visitors know AI assistants, not the word "MCP": the site says "connecteur".

## Product Purpose

A free, open-source MCP connector that lets an assistant fetch real roll-call votes (scrutins), deputies and groups from the Assemblée nationale open data, through the public CIVIX API, and cite the source of each vote instead of answering from memory. The landing page explains it, proves it with live data, and gets the visitor to add the connector (copy `https://mcp-assemblee-nationale.vercel.app/mcp`, follow per-assistant steps). Success: the address is copied or install steps are opened.

## Positioning

Independent and non-official. Every figure is read live from the official open data and every answer links to the vote's page on assemblee-nationale.fr and CIVIX. No ranking, no scoring, no political interpretation.

## Operating Context

Traffic from social networks, GitHub, word of mouth, data.gouv.fr *(inferred)*. Install happens inside the assistant's connector settings (Claude, ChatGPT paid plans in the browser, Gemini CLI, local `uvx`). The connector exposes 25 read-only tools and 6 prompt templates; each analysis ends with a "Méthode" block.

## Capabilities and Constraints

- Live data only: home page ISR every 30 min, client polling every 3 min (`/api/live`), demo and deputy autocomplete through `/api/demo` and `/api/deputes`. Fallback "Données momentanément indisponibles" when CIVIX is down at build.
- Pages: home, `/scrutins/[uid]`, `/confidentialite`, `/mentions`, 404, error, OG image, sitemap, robots.
- Security posture already audited: strict CSP (`default-src 'self'`, `font-src 'self'`), cross-site guard on API routes, zod validation, URL allowlist. No external scripts, fonts, images or analytics.
- Fonts self-hosted, open licence.

## Brand Commitments

- Name: "MCP Assemblée nationale". French copy only.
- Visible line on every page: "Projet indépendant et non officiel · données de l'Assemblée nationale via CIVIX".
- No State impersonation: no "République Française" block, no Marianne font or logo, no tricolour, no ".gouv" in the UI.
- Neutrality is absolute: no ranking of deputies or groups, no loaded adjectives, vote positions never green/red; pour / contre / abstention encoded by shape and tone.
- Owner's palette request: data.gouv.fr colorimetry (white page, `#f6f6f6` surfaces, `#161616` / `#3a3a3a` / `#666666` text, `#e5e5e5` borders, Bleu France `#000091` accent; DSFR dark values for the dark theme). Light theme is the default on first visit; a "Paramètres d'affichage" dialog offers clair / sombre / système.
- Copy style: compound words rewritten to avoid hyphens where possible; no invented proof.

## Evidence on Hand

Only live CIVIX data: counters (scrutins of the legislature, latest vote date, deputies, groups), this week's votes grouped by dossier, votes per day over 30 days, most voted dossiers (7 / 30 days), adoption rate by vote type, latest final votes with counts, group composition, a hero chat example built from a real final vote and a real deputy's recorded position. There are no testimonials, usage numbers, customer logos or press. Never fabricate any.

## Product Principles

1. Prove with the record, never claim: every number on screen comes from the source and links to it.
2. Neutral by construction: the design never ranks, colours or editorialises a vote.
3. Plain French for non-technical people: "connecteur", not "MCP server".
4. One action: add the connector to your assistant.
5. Unmistakably independent: credible and public-interest, never official-looking.

## Accessibility & Inclusion

WCAG AA contrast in both themes, full keyboard use, visible focus, reduced motion respected, text alternatives for every chart, semantic landmarks and a skip link.
