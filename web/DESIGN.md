# Page d'accueil, décisions de conception

Suit la skill `landing-page-design` (partie A puis partie B). Les règles données par le propriétaire du projet l'emportent en cas de conflit : aucune preuve inventée, mots composés réécrits dans les textes, neutralité stricte.

## Hypothèses d'entrée (A1)

- Action principale unique : ajouter le connecteur à son assistant (bouton « Ajouter à mon assistant », cible `#installer`). Conversion : adresse copiée ou étapes d'installation ouvertes.
- Offre : gratuit, sans compte, sans clé, lecture seule, chaque réponse sourcée.
- Public : citoyens sans bagage technique, puis journalistes, enseignants, étudiants, associations civiques.
- Objections : trop technique, fiable et neutre, payant, données personnelles, compatibilité avec mon assistant.
- Preuves : uniquement des données réelles, lues en direct sur CIVIX au build puis toutes les 30 minutes. Aucun témoignage, logo, chiffre d'usage ni personne inventés.
- Trafic : réseaux sociaux, GitHub, bouche à oreille, data.gouv.fr. Les visiteurs connaissent les assistants IA, pas le mot MCP : on dit « connecteur ».
- Direction : éditorial minimal, thèmes clair et sombre selon `prefers-color-scheme`, mobile d'abord.

## 1. Plan de la page

Layout **B, récit long**. Le produit ne se comprend pas depuis une capture : il faut expliquer ce qu'est un connecteur, rassurer sur la neutralité et la fiabilité, puis prouver avec des données réelles. Le public est sceptique et peu technique, ce qui justifie un récit qui éduque avant de demander l'action.

1. Barre de navigation flottante (translucide, flou), lien GitHub en icône
2. **Hero** : titre, sous titre, CTA unique, preuve en direct, échange de chat réel
3. **Problème et solution** : un assistant seul répond de mémoire, avec le connecteur il va chercher
4. **Bénéfices** (4)
5. **Comment ça marche** (3 étapes)
6. **Révélation du slogan** (mot par mot au défilement)
7. **Preuve en direct** : « Cette semaine à l'Assemblée », tendances (votes par jour sur 30 jours, textes les plus votés 7 et 30 jours, taux d'adoption par type de vote, derniers votes sur l'ensemble d'un texte), composition des groupes
8. **Démo en direct** : « Comment a voté [député] sur [sujet] ? »
9. **Ce que le connecteur sait faire** : 12 outils et 3 questions prêtes à l'emploi, formulés comme des questions
10. **Installer** (cible du CTA) : Claude, ChatGPT, Gemini, en local, avec copie de l'adresse
11. **Garanties** (réduction du risque) : gratuit, sans compte, code ouvert, lecture seule
12. **FAQ** (10 questions, JSON-LD FAQPage)
13. **CTA final** identique au premier
14. Pied de page : GitHub, source des données, licence, confidentialité, mentions

Pages annexes : `/scrutins/[uid]` (détail d'un vote), `/confidentialite`, `/mentions`, 404 de marque, `opengraph-image`, `sitemap.xml`, `robots.txt`, icône.

## 2. Copie du hero

- **Titre** : « Sachez comment ont voté vos députés, source à l'appui » (coupures : après « voté »).
- **Sous titre** : « Ajoutez un connecteur gratuit à votre assistant IA. Il va chercher les vrais scrutins de l'Assemblée nationale au lieu de répondre de mémoire, et il cite le lien de chacun. »
- **CTA** : « Ajouter à mon assistant »
- **Réassurance sous le CTA** : « Gratuit, sans compte, sans clé. Pour Claude et ChatGPT. »
- **Preuve en direct** : « {N} scrutins sous la 17e législature, dernier vote le {date} » (chiffres lus sur CIVIX).
- **Visuel** : un échange de chat construit avec un vrai scrutin récent (dernier vote sur l'ensemble d'un texte) et la vraie position d'un vrai député. Légende : « Exemple construit avec les données du {date} ». Si CIVIX est injoignable, le visuel passe en état d'erreur composé et ne montre aucune donnée.

## 3. Bénéfices

1. **Des réponses avec leur source.** Chaque scrutin cité renvoie vers la page de l'Assemblée et celle de CIVIX.
2. **Les vrais chiffres, pas un souvenir.** Pour, contre, abstentions et détail par groupe viennent des données ouvertes, lues au moment de la question.
3. **Gratuit et sans compte.** Une adresse à coller. Pas de clé, pas d'inscription, aucune donnée personnelle demandée.
4. **Des faits, sans classement.** Aucun député ni groupe n'est noté. Le connecteur transmet les positions telles qu'elles sont enregistrées.

## 4. Comment ça marche

1. **Copiez l'adresse** du connecteur (un bouton le fait pour vous).
2. **Collez l'adresse dans votre assistant**, dans les réglages des connecteurs (Claude ou ChatGPT).
3. **Posez votre question** en français : « Comment a voté ma députée sur le budget ? »

Définition de « connecteur » (une phrase) : « Un connecteur est une adresse que votre assistant sait interroger pour obtenir des données fiables ; son nom technique est MCP. »

## 5. Slogan (révélation mot par mot)

« Les chiffres viennent de l'Assemblée. Les liens mènent à la source. Le jugement vous appartient. »

## 6. FAQ

1. **Que fait ce connecteur, concrètement ?** Il permet à votre assistant de consulter les scrutins, les députés et les groupes de l'Assemblée nationale pendant la conversation, puis de citer ses sources.
2. **Combien ça coûte ?** Rien. Le connecteur, l'API et l'hébergement sont gratuits. Seul l'abonnement à votre assistant peut être payant : ChatGPT demande un plan payant pour les connecteurs personnalisés.
3. **C'est trop technique pour moi ?** Non. Il suffit de copier une adresse et de la coller dans les réglages de votre assistant. Les étapes sont détaillées plus haut.
4. **Les réponses sont fiables et neutres ?** Les chiffres viennent des données ouvertes de l'Assemblée nationale et sont transmis tels quels, sans note ni classement. L'assistant rédige la phrase : ouvrez le lien source pour vérifier.
5. **Que deviennent mes données ?** Le serveur reçoit seulement la recherche envoyée par l'assistant, jamais votre conversation. Pas de compte, pas de cookie, pas d'historique conservé.
6. **Ça marche avec mon assistant ?** Claude (y compris le plan gratuit, avec un connecteur personnalisé) et ChatGPT (plans payants, depuis le navigateur). L'application Gemini ne prend pas en charge les connecteurs personnalisés à notre connaissance ; Gemini CLI fonctionne.
7. **L'assistant peut quand même se tromper ?** Oui, il peut mal résumer. C'est pourquoi chaque réponse cite la page du scrutin, à vérifier.
8. **D'où viennent les chiffres ?** De l'Assemblée nationale, reprise par l'API publique CIVIX référencée sur data.gouv.fr, sous Licence Ouverte Etalab 2.0.
9. **Ce projet est officiel ?** Non. Projet personnel et indépendant, sans lien avec l'Assemblée nationale ni avec CIVIX.
10. **Et le Sénat ?** Pas pour l'instant : seule l'Assemblée nationale est couverte.

## 7. SEO et AEO

- **Indexer** : offre durable, intention de recherche alignée (« comment a voté un député », « votes Assemblée nationale IA »).
- **Title** : « Comment ont voté vos députés ? Posez la question à votre assistant IA »
- **Meta description** : « Connecteur gratuit pour Claude et ChatGPT : les votes des députés de l'Assemblée nationale, chiffres officiels et source de chaque scrutin. Sans compte. »
- FAQ en questions et réponses visibles, balisage `FAQPage` JSON-LD, `WebSite` et `SoftwareApplication` minimal, OG image dynamique avec les chiffres du jour, `sitemap.xml`, `robots.txt`, liens internes vers `/scrutins/[uid]`.
- Pages `/confidentialite` et `/mentions` indexables. `/api/*` exclu par `robots.txt`.

## 8. Recommandation de layout

**B, récit long.** Voir la section 1. Le hero reste de type A (message, preuve, visuel) mais la page enchaîne problème, bénéfices, explication, preuve en direct, démo, installation et FAQ pour lever le scepticisme avant la demande d'action.

## 9. Système visuel (partie B), décisions

- Police unique : Geist (paquet `geist`, `next/font/local`). Geist Mono uniquement pour les chiffres et données. Pas d'italique, poids maximum bold.
- Échelle de texte : classes Tailwind `text-xs` à `text-6xl` uniquement. Titres `text-4xl` à `text-6xl`, corps `text-base` ou `text-lg`.
- Espacements : uniquement les valeurs 0, 0.5, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24 de l'échelle Tailwind (2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96 px). Boutons principaux : `px-3 py-2`, `text-base font-semibold`.
- Rayons : échelle Tailwind. Règle d'imbrication appliquée quand l'écart est inférieur à 32 px : carte `rounded-2xl` (16) avec `p-2` (8) donne `rounded-lg` (8) à l'intérieur ; carte `rounded-3xl` (24) avec `p-4` (16) donne `rounded-lg` (8) ; `rounded-xl` (12) avec `p-2` donne `rounded-sm` (4). Quand le résultat est inférieur ou égal à 2, l'élément intérieur reste carré.
- Fonds sombres : seulement `#000000`, `#181818`, `#1F1F1F`, `#272727`, `#313131`, `#131209`. Aucun dégradé de fond. Le seul dégradé est le texte du titre du hero (blanc vers `#9B9B9B` en sombre, noir vers `#666666` en clair).
- Bordures : toujours sur les quatre côtés.
- Marques de données (barres, points de légende) : dessinées en SVG avec `fill`, hors des fonds de surface. Couleurs de position non connotées (bleu, ambre, gris), jamais vert ou rouge. Adopté et rejeté sont distingués par une icône et un mot, pas par une couleur.
- Mouvement : courbe `cubic-bezier(0.22, 1, 0.36, 1)` exposée comme jeton `ease-weighted` et appliquée par défaut à toutes les transitions, `duration-500` pour les positions, `duration-300` pour les couleurs. Seulement `transform` et `opacity`. `prefers-reduced-motion` remplace les déplacements par un simple fondu. Révélations avec `IntersectionObserver`, une seule fois.
- Navigation : barre flottante centrée, translucide avec flou, icône de menu animée, panneau mobile pleine hauteur, liens qui entrent à 60 ms d'intervalle (plafond 400 ms), page courante indiquée.

## 10. Données en direct et appels CIVIX

Voir `README.md` pour la liste des appels par rendu et les durées de cache.

## Résultat de la checklist

Vérifié par grep sur `src/` et par lecture. Pass sauf mention.

Stratégie
- Une offre, un public, une action : pass (CTA « Ajouter à mon assistant », cible `#installer`)
- Pas de CTA concurrent au dessus de la ligne de flottaison : pass (le CTA de la barre est masqué sous `lg`, GitHub en icône discrète)
- Chiffres précis plutôt que verbes vagues : pass (compteurs lus en direct, 12 outils, 3 modèles)
- Au moins une réduction de risque : pass (section garanties)
- Preuve à côté de l'affirmation : pass (chiffres en direct dans les bénéfices et le hero)
- Layout choisi : pass (B)

Visuel
- Police unique, pas d'italique, pas d'ultra gras : pass (Geist, `font-medium/semibold/normal` seulement ; Geist Mono pour les chiffres ; `em, i, cite` forcés en normal)
- Pas de trait d'union dans les textes, pas de mot orphelin : pass (grep des motifs courants, `text-wrap: balance/pretty`). Restent les noms propres et titres venant de l'API
- Tailles sur l'échelle Tailwind : pass (`text-xs` à `text-6xl`, aucun `-[`)
- Espacements de la table : pass (grep des valeurs hors table : `pt-32` et `pt-40` ramenés à `pt-24`, `max-h-64` remplacé par la classe `listbox-height`)
- Rayons imbriqués : pass avec réserve (cartes `rounded-2xl` + `p-2` + intérieur `rounded-lg`, onglets `rounded-xl` + `p-1` + `rounded-lg`) ; les étiquettes en `rounded-sm` à l'intérieur de cartes à marge 16 px ou plus restent hors formule
- Pas de bordure sur un seul côté, pas de dégradé de fond : pass (seul dégradé : texte du titre, classe `.hero-title`)
- Titre et sous titre du hero plafonnés à 680 px : pass (`max-w-hero`, jeton de thème)
- Icônes Phosphor : pass
- Transitions sur la courbe B7, révélations par IntersectionObserver : pass (courbe posée comme défaut du thème ; aucun écouteur `scroll`)
- Révélation du slogan mot par mot : pass (3 phrases, un IntersectionObserver par mot, repli sans mouvement pour `prefers-reduced-motion`)
- Fonds sombres limités à la liste : pass pour les surfaces (`#131209`, `#181818`, `#1F1F1F`, `#272727`, `#313131`) ; les marques de données SVG (bleu, ambre, gris) sont des remplissages hors surface

Contenu et finitions
- Vraie copie, aucun mot interdit : pass (aucune personne, citation, logo ni statistique inventés)
- États survol, actif, focus, chargement, vide, erreur : pass (squelettes de la démo, états vides et erreurs composés, repli « Données momentanément indisponibles »)
- Pas de lien mort, page courante indiquée : pass (suivi de section dans la barre, `aria-current`)
- 404, mentions légales, confidentialité, validation de formulaire, favicon, balises meta, textes alternatifs : pass (`not-found.tsx`, `/mentions`, `/confidentialite`, validation du formulaire de démo, `icon.svg`, OG dynamique)

Non vérifié : rendu visuel clair et sombre sur tous les écrans, lecteur d'écran, Lighthouse. Un contrôle visuel mobile du hero a été fait dans Chrome.
