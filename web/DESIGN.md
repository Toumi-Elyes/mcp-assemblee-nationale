---
name: MCP Assemblée nationale
description: Les votes des députés, affichés comme un tableau des départs, dans la colorimétrie de data.gouv.fr.
colors:
  bg: "#ffffff"
  surface: "#f6f6f6"
  raised: "#ffffff"
  hover: "#eeeeee"
  line: "#e5e5e5"
  rule: "#161616"
  ink: "#161616"
  ink-soft: "#3a3a3a"
  muted: "#666666"
  accent: "#000091"
  accent-hover: "#1212ff"
  accent-active: "#2323ff"
  on-accent: "#ffffff"
  flap: "#161616"
  flap-ink: "#ffffff"
  flap-split: "#3a3a3a"
  mark-pour: "#000091"
  mark-contre: "#3a3a3a"
  mark-abstention: "#868686"
  mark-absent: "#e5e5e5"
  bg-dark: "#161616"
  surface-dark: "#1e1e1e"
  raised-dark: "#242424"
  hover-dark: "#2a2a2a"
  line-dark: "#353535"
  rule-dark: "#cecece"
  ink-dark: "#ffffff"
  ink-soft-dark: "#cecece"
  muted-dark: "#a6a6a6"
  accent-dark: "#8585f6"
  accent-hover-dark: "#a5a5fa"
  accent-active-dark: "#c1c1fb"
  on-accent-dark: "#161616"
  flap-dark: "#2e2e2e"
  flap-split-dark: "#161616"
  mark-pour-dark: "#8585f6"
  mark-contre-dark: "#cecece"
  mark-abstention-dark: "#7b7b7b"
  mark-absent-dark: "#353535"
typography:
  display:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, sans-serif"
    fontSize: "4.5rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, sans-serif"
    fontSize: "3rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  board:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.5
    fontFeature: "\"tnum\""
  body:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  lead:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.55
  small:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.43
  label:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.43
    letterSpacing: "0.025em"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
rounded:
  flap: "0.06em"
  sm: "4px"
  full: "9999px"
spacing:
  flap-gutter: "0.06em"
  row: "14px"
  gutter-mobile: "16px"
  gutter: "24px"
  section-mobile: "64px"
  section: "80px"
  measure: "40rem"
  page: "80rem"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.sm}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-primary-active:
    backgroundColor: "{colors.accent-active}"
  button-secondary:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.accent}"
    rounded: "{rounded.sm}"
    padding: "10px 16px"
  button-secondary-hover:
    backgroundColor: "{colors.hover}"
  flap-cell:
    backgroundColor: "{colors.flap}"
    textColor: "{colors.flap-ink}"
    typography: "{typography.display}"
    rounded: "{rounded.flap}"
  result-tile:
    backgroundColor: "{colors.flap}"
    textColor: "{colors.flap-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "2px 6px"
  copy-field:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    typography: "{typography.mono}"
    rounded: "{rounded.sm}"
    padding: "10px 12px"
  install-stop:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    size: "28px"
  install-stop-current:
    backgroundColor: "{colors.rule}"
    textColor: "{colors.bg}"
    rounded: "{rounded.full}"
    size: "28px"
---

# Design System: MCP Assemblée nationale

## Overview

**Creative North Star: "Le tableau des départs de l'Assemblée"**

Le registre de l'Assemblée affiché comme un tableau des départs de gare, posé sur une page éditoriale blanche. Les scrutins arrivent en lignes classées par l'heure, les plus récents en tête, chacun avec son volet d'état. Les chiffres se retournent dans des tuiles à palettes quand la donnée en direct change. L'installation est une ligne à trois arrêts, dès le premier écran (copier, coller, demander) et de nouveau en clôture de page. Le monde est celui de l'affichage public d'information : lisible de loin, factuel, sans commentaire.

La densité est celle d'un horaire : des filets pleine largeur, des colonnes, aucune boîte. La couleur est presque absente. L'encre et le papier portent tout, et le Bleu France n'apparaît que là où l'on peut agir. La colorimétrie reprend celle de data.gouv.fr (valeurs du système de design de l'État pour le thème sombre). Le projet s'en sert comme d'une palette, jamais comme d'une identité : rien ne doit faire croire à un site officiel.

Refus confirmés : le hero partagé avec une capture de produit dans une boîte, puis des bandes alternées de cartes à icônes sous des surtitres ; le vert et le rouge pour les positions de vote ; tout signe de l'État (Marianne, bande tricolore, bloc « République Française », « .gouv »).

**Key Characteristics:**
- Page blanche, lignes réglées pleine largeur, aucune carte.
- Tuiles à palettes encre et blanc pour les comptes, les dates et les états seulement.
- Bleu France réservé aux actions, aux liens et à la marque « pour ».
- Barlow Semi Condensed pour la signalétique, Public Sans pour la lecture.
- Encodage des votes neutre : la forme porte l'information, jamais une couleur partisane.
- Clair par défaut, quel que soit le réglage de l'appareil.

## Colors

Une palette d'encre sur papier, d'un seul bleu, empruntée à data.gouv.fr ; le thème sombre reprend les valeurs sombres du système de design de l'État (jetons `-dark`).

### Primary
- **Bleu France** (accent ; accent-dark en sombre) : boutons, liens, anneau de focus, sélection de texte, curseur, puces radio, et la marque « pour ». Survol et appui passent aux deux bleus plus vifs (accent-hover, accent-active). Le texte posé sur le bleu est blanc en clair, encre en sombre (on-accent).

### Neutral
- **Papier** (bg) : le fond de la page et des lignes du tableau.
- **Gris de passage** (surface) : le fond de la seule section dense de données en direct (tendances, composition des groupes).
- **Papier relevé** (raised) : la boîte de dialogue et la liste de suggestions, seuls calques flottants.
- **Gris de survol** (hover) : survol des boutons secondaires, des options et du bouton fermer ; fond des squelettes de chargement.
- **Filet** (line) : les filets fins de 1 px entre les lignes, les pistes vides des barres.
- **Trait d'encre** (rule) : les filets épais de 2 px qui ouvrent une section, un tableau ou la ligne d'installation ; la ligne et les arrêts du schéma ; le soulignement de l'onglet ou de la page courante.
- **Encre** (ink), **encre douce** (ink-soft), **gris de légende** (muted) : titres et chiffres ; textes d'appoint ; légendes, têtes de colonnes et métadonnées.
- **Tuile** (flap, flap-ink, flap-split) : tuiles encre à chiffres blancs, coupées par un trait au milieu. En sombre, la tuile s'éclaircit (flap-dark) et le trait de coupe prend la couleur du fond.

### Marques de vote
- **Pour** (mark-pour) : aplat Bleu France.
- **Contre** (mark-contre) : hachures diagonales à 45° de 2 px sur 4 px, dessinées par le motif SVG `pattern-contre` défini une seule fois dans le document, sur le fond de page.
- **Abstention** (mark-abstention) : aplat gris moyen.
- **Non votant** (mark-absent) : aplat pâle, couleur du filet. C'est une piste, pas une marque lue seule : l'effectif est toujours écrit dans la légende.

### Named Rules
**The Bleu d'action Rule.** Le Bleu France ne colore que ce qu'on peut presser ou suivre, plus la marque « pour ». Les barres de tendance, d'adoption et de dossiers sont en encre sur piste pâle, jamais en bleu.

**The Gris de passage Rule.** Le gris de passage est réservé au fond de la section de données en direct. Aucune autre section ne prend de fond gris ; le rythme vient des filets, pas de bandes alternées.

**The Ni vert ni rouge Rule.** Pour, contre, abstention et non votant s'encodent par la forme (aplat, hachures, gris, pâle), avec libellés et effectifs dans la légende. Les couleurs d'information (vert, rouge, orange) ne sont jamais utilisées pour un vote ou un résultat.

**The Pas d'État Rule.** La colorimétrie de data.gouv.fr est une palette, pas un costume : pas de Marianne, pas de bande tricolore, pas de « République Française », pas de « .gouv ». La ligne « Projet indépendant et non officiel · données de l'Assemblée nationale via CIVIX » reste visible en tête de chaque page.

**The Clair d'abord Rule.** Le thème clair s'affiche à la première visite, quel que soit le réglage de l'appareil. Le choix (clair, sombre, système) se fait dans « Paramètres d'affichage », est gardé dans `localStorage` sous la clé `theme`, et un script en ligne dans `<head>` pose `data-theme` sur `<html>` avant le premier affichage dès qu'un choix existe. Les jetons sombres s'appliquent sous `[data-theme="dark"]`, et sous `[data-theme="system"]` quand l'appareil préfère le sombre.

## Typography

**Display Font:** Barlow Semi Condensed (repli Public Sans, sans serif), poids 500, 600 et 700
**Body Font:** Public Sans (repli ui-sans-serif, system-ui), poids 400, 500 et 700
**Label/Mono Font:** mono système (ui-monospace, SFMono-Regular, Menlo)

**Character:** Une grotesque de signalétique, étroite et ferme, pour tout ce qui s'affiche (titres, texte du tableau, chiffres), et une sans serif civique, sobre, pour tout ce qui se lit. Les deux polices sont auto hébergées via `@fontsource`, sous une CSP stricte (`font-src 'self'`) : aucun service de polices externe.

### Hierarchy
- **Display** (Barlow 600, 4.5rem sur grand écran, 3.75rem puis 2.25rem en dessous, interligne 1, approche serrée) : le titre principal de l'accueil, en deux lignes.
- **Headline** (Barlow 600, 2.25rem à 3rem, approche serrée) : titres de section ; 1.875rem à 2.25rem pour le titre du tableau « Cette semaine à l'Assemblée » et les sections de la page d'un scrutin.
- **Title** (Barlow 600, 1.25rem à 1.5rem) : titres de tableaux numérotés, arrêts de la ligne, questions de la FAQ, nom du site.
- **Board** (Barlow 600, 1.125rem, chiffres tabulaires) : dates des lignes du tableau, sigles et effectifs des groupes, libellés à côté d'une tuile.
- **Body** (Public Sans 400, 1rem, interligne 1.5) : texte courant et titres des scrutins (500), mesure de 40rem.
- **Lead** (Public Sans 400, 1.125rem) : introductions de section, en encre douce.
- **Small** (Public Sans 400, 0.875rem) : légendes, effectifs, métadonnées ; 0.75rem pour la ligne non officielle.
- **Label** (Barlow 600, 0.875rem, capitales, interlettrage 0.025em) : têtes de colonnes du tableau, interlocuteurs de l'exemple de conversation (« Vous », « Votre assistant ») et libellés des tuiles de résultat. Rien d'autre.
- **Mono** (0.875rem) : l'adresse du connecteur, les noms d'outils et de modèles, les blocs de code. Jamais pour les chiffres.

### Named Rules
**The Signalétique Rule.** Un chiffre qui s'affiche seul (tuile, date du tableau, effectif d'un groupe, libellé à côté d'une tuile) est en Barlow Semi Condensed à chasse tabulaire. Un chiffre pris dans une phrase de lecture (décomptes d'une ligne, légende, part d'un groupe, compte d'un dossier) reste en Public Sans à chasse tabulaire. Le mono ne sert qu'aux adresses, aux noms d'outils et au code.

**The Pas d'italique Rule.** `em`, `i`, `cite` et `address` sont forcés en romain. Les titres sont équilibrés (`text-wrap: balance`), les paragraphes soignés (`text-wrap: pretty`).

## Layout

Une page de 80rem au plus, avec 16 px de marge sur téléphone et 24 px au delà. La grille est à 12 colonnes sur grand écran : le premier écran doit faire comprendre le service à une personne qui n'a jamais entendu le mot « connecteur » : le titre sur deux lignes, une phrase sans jargon, puis « Comment ça marche » en trois étapes (le champ d'adresse avec « Copier l'adresse » sur la première) sur 7 colonnes ; l'exemple de conversation, court (question, réponse en une phrase, lien vers le vote), sur les 5 autres. Juste après vient « En clair » : les questions de base (c'est quoi, à quoi ça sert, combien, faut il s'y connaître, quel assistant) toujours ouvertes, et un lexique des mots du site (scrutin, législature, groupe, connecteur, CIVIX). Puis la vidéo (50 s, 47 s en vertical), où chaque écran reste affiché le temps de le lire, avec son texte écrit à côté. Le tableau de la semaine vient ensuite sur 8 colonnes : les cinq scrutins les plus récents (titres limités à deux lignes, titre complet au survol et sur la page du scrutin), le reste derrière « Afficher … autres scrutins », avec le compteur à palettes sur les 4 autres. Retour d'un visiteur non technique (octobre 2026) : le service n'était pas compris, les explications étaient en bas de page et la vidéo allait trop vite. Ne pas revenir à un premier écran limité à l'adresse. La navigation compte quatre liens. Les sections respirent de 80 px (112 px dès 640 px) ; seule la partie données reste dense. Elles s'ouvrent par un en tête posé sur un trait d'encre de 2 px : titre à gauche, métadonnées alignées à droite sur grand écran. Le texte de lecture ne dépasse pas 40rem.

Le tableau des scrutins a trois colonnes dès 640 px : date (4.5rem), scrutin (le reste), résultat (6.5rem, aligné à droite), avec 20 px entre colonnes et 14 px de hauteur de ligne de part et d'autre. Sur téléphone, la date et le résultat partagent une ligne au dessus du titre. Les lignes sont regroupées par dossier : les dossiers sont classés par leur vote le plus récent, et dans chaque dossier le vote sur l'ensemble du texte vient en tête, puis les autres scrutins du plus récent au plus ancien.

La ligne d'installation est verticale sur téléphone (arrêts à gauche, trait vertical) et horizontale sur grand écran (colonnes proportionnelles, trait horizontal). Le dernier tronçon s'efface en filet fin.

### Named Rules
**The Lignes réglées Rule.** On sépare par des filets pleine largeur, jamais par des boîtes : 2 px d'encre pour ouvrir, 1 px de filet entre les lignes. Pas de grille de cartes.

**The Chronologie Rule.** La profondeur est le temps : dossiers et scrutins se suivent du plus récent au plus ancien, avec pour seule exception le vote sur l'ensemble d'un texte, placé en tête de son dossier. Aucune autre mise en avant éditoriale.

## Elevation & Depth

Le système est plat : aucune ombre, aucun flou, aucun dégradé sur la page. La hiérarchie passe par l'épaisseur des filets (2 px contre 1 px), par le contraste encre et papier, et par l'unique fond gris de la section de données. Seuls les deux calques qui flottent réellement au dessus de la page portent une ombre : la boîte de dialogue « Paramètres d'affichage », sur un voile noir à 50 %, et la liste de suggestions du champ député de la démonstration (valeurs dans le fichier annexe).

### Named Rules
**The Calque seulement Rule.** Une ombre signale un calque qui recouvre la page (dialogue, liste déroulante), jamais une surface posée dessus. Aucune carte, aucun bouton, aucune tuile n'a d'ombre.

## Shapes

Des formes d'affichage public : rectangles nets, angles à peine adoucis. Boutons, champs, options du dialogue et tuiles de résultat ont 4 px de rayon. Les cellules à palettes ont un rayon proportionnel au corps (0.06em) et sont séparées par un intervalle proportionnel (0.06em), pour garder la même forme à toutes les tailles. La boîte de dialogue et la liste de suggestions restent carrées, bordées d'un trait d'encre. Seuls les arrêts de la ligne d'installation et le point d'état du direct sont ronds. Les marques de données sont des rectangles : segments de barre, et un carré de 6 px par siège dans la grille des groupes.

## Components

### Buttons
Fermes et pleins, jamais en pilule.
- **Shape:** angles légèrement adoucis (4 px).
- **Primary:** aplat Bleu France, texte blanc en gras, 10 px sur 16 px, corps 1rem (0.875rem en petite taille). C'est l'action « Copier l'adresse » et les relances des pages d'erreur.
- **Hover / Focus:** le bleu s'avive au survol puis à l'appui, transition de couleur de 150 ms. Le focus est un contour de 2 px Bleu France décalé de 2 px, partout.
- **Secondary:** fond papier, filet Bleu France de 1 px, texte bleu ; fond gris de survol. La petite variante a un filet pâle qui passe au bleu au survol.
- **Copier attaché:** collé au champ d'adresse, il partage son bord et perd son arrondi de jonction.

### Links
- Texte Bleu France souligné (1 px, décalé de 0.2em, 2 px au survol). Les titres des scrutins sont en encre avec un soulignement pâle, et passent au bleu au survol. Les liens externes portent une icône Phosphor de sortie.

### Inputs / Fields
- **Style:** fond papier, trait d'encre de 1 px, 4 px de rayon. L'adresse du connecteur est en mono, en lecture seule. Le champ « député » de la démonstration est une ligne de saisie en Barlow 1.5rem posée sur un trait d'encre de 2 px.
- **Focus:** contour Bleu France de 2 px. Les filtres passent leur bordure au bleu au survol.
- **Erreur:** message relié au champ ; aucune couleur rouge.

### Navigation
- Ligne non officielle en tête (corps 0.75rem ; le build la pose aujourd'hui sur le gris de passage, écart à la règle du même nom, non canonisé), avec « Paramètres d'affichage » et « Code source » en bleu à droite (icône seule sur téléphone, nom accessible gardé). En dessous, un en tête blanc à filet inférieur : le nom du site en Barlow 700, et des liens en Barlow 600 qui défilent horizontalement sur téléphone. La page courante est soulignée d'un trait d'encre de 2 px. Les onglets (assistants, périodes) suivent la même règle : trait d'encre sous l'onglet choisi, gris de légende sinon.

### Tuile à palettes (signature)
Un caractère par cellule : aplat encre, chiffre blanc en Barlow tabulaire, trait de coupe horizontal au milieu (1 px au moins). Les espaces deviennent des intervalles vides. Réservée aux comptes, aux dates et aux numéros (compteur de la législature, total de la semaine, numéro d'un scrutin, 404). À l'affichage, chaque caractère se retourne ; quand l'actualisation apporte une valeur changée, seuls les caractères modifiés se retournent : rotation de -50° à 0° avec un léger rebond, 520 ms, courbe ease-out-quint, 40 ms de décalage par caractère. Le chiffre reste lisible pendant tout le mouvement (aucune opacité nulle). Sous `prefers-reduced-motion`, aucun mouvement. Le groupe porte un nom accessible avec la valeur complète.

### Tuile de résultat
« Adopté » et « Rejeté » partagent la même tuile encre : Barlow 600 en capitales, 4 px de rayon, et ne diffèrent que par l'icône (coche ou croix, Phosphor en gras) et le mot. « Inconnu » prend un point d'interrogation.

### Barre de positions
Une barre pleine largeur (8 px dans les lignes, 24 px en grand) qui juxtapose pour, contre, abstention et non votant dans cet ordre, avec les marques décrites dans Colors. Elle porte un nom accessible chiffré. Sa légende est en pastilles de 12 px cerclées d'encre douce, suivies du libellé et de l'effectif.

### Grille des sièges
Pour chaque groupe, une ligne réglée : sigle et nom, un carré d'encre par siège (50 par ligne), effectif et part. Les groupes sont classés par effectif, avec une légende qui dit que cet ordre ne reflète pas la place dans l'hémicycle. Elle remplace l'hémicycle, parce que CIVIX ne fournit aucun ordre de placement.

### Ligne d'installation
Trois arrêts ronds de 28 px numérotés en Barlow gras, reliés par un trait d'encre de 2 px. L'arrêt de départ est plein (encre, chiffre papier), les suivants sont évidés. Le premier arrêt porte le champ d'adresse et « Copier l'adresse », le deuxième le lien vers les étapes par assistant.

### Tableaux numérotés
Les figures de données ouvrent par un trait d'encre de 2 px, un titre en Barlow 1.5rem, puis une légende « Tableau N. » en gras suivie d'une note. Le numéro vient sous le titre, jamais au dessus.

## Do's and Don'ts

### Do:
- **Do** séparer par des filets pleine largeur : 2 px d'encre pour ouvrir une section ou un tableau, 1 px de filet entre les lignes.
- **Do** réserver le Bleu France aux boutons, aux liens, au focus et à la marque « pour ».
- **Do** encoder pour en aplat bleu, contre en hachures diagonales, abstention en gris (#868686 en clair, #7b7b7b en sombre) et non votant en pâle, avec libellés et effectifs dans la légende.
- **Do** distinguer adopté et rejeté par l'icône et le mot, dans des tuiles d'encre identiques.
- **Do** mettre les comptes, les dates et les numéros dans des tuiles à palettes, et couper le retournement sous `prefers-reduced-motion`.
- **Do** afficher le thème clair à la première visite et garder le choix sous la clé `theme`, appliqué avant le premier affichage.
- **Do** n'afficher que des données réelles de CIVIX, avec un état « Données momentanément indisponibles » quand elles manquent.
- **Do** garder la ligne « Projet indépendant et non officiel » visible en tête de chaque page.

### Don't:
- **Don't** utiliser le vert ou le rouge (ni aucune couleur d'information) pour une position ou un résultat.
- **Don't** utiliser Marianne, une bande tricolore, un bloc « République Française » ou « .gouv » dans l'interface.
- **Don't** poser un surtitre en capitales au dessus d'un titre : les capitales Barlow sont réservées aux têtes de colonnes, aux interlocuteurs et aux tuiles de résultat.
- **Don't** construire des grilles de cartes ni des bandes alternées de fonds gris ; le gris de passage n'appartient qu'à la section de données en direct.
- **Don't** dessiner un hémicycle ni rien qui suggère une place politique : CIVIX ne donne aucun ordre de placement.
- **Don't** mettre d'ombre, de flou ou de dégradé sur une surface de la page ; l'ombre est réservée aux calques (dialogue, liste de suggestions).
- **Don't** utiliser le mono pour les chiffres, ni charger une police depuis un service externe.
- **Don't** inventer de preuve : ni témoignage, ni logo, ni chiffre d'usage.
