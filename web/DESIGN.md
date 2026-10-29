# Page d'accueil, décisions de conception

> Dernière révision : style data.gouv.fr (section « Révision v3 »). Les sections plus bas qui parlent de Geist, de l'accent sarcelle, de la barre flottante ou des animations de révélation décrivent l'état précédent.

Suit la skill `landing-page-design` (partie A puis partie B). Les règles données par le propriétaire du projet l'emportent en cas de conflit : aucune preuve inventée, mots composés réécrits dans les textes, neutralité stricte.

## Révision v3 : style graphique de data.gouv.fr (remplace les décisions visuelles précédentes)

Consigne du propriétaire : reprendre la colorimétrie d'origine de data.gouv.fr et son style graphique, parce que la version précédente faisait « trop IA ». Cette section l'emporte sur la skill pour tout ce qui est visuel, et sur les sections « Direction artistique », « Système visuel », « Audit d'accessibilité » et les maquettes plus bas, qui décrivent l'état précédent (barre flottante, accent sarcelle, Geist, révélations animées). Structure, données, textes, routes et tests restent inchangés.

### Palette (jetons dans `globals.css`)

| Jeton | Clair | Sombre | Usage |
|---|---|---|---|
| fond | `#FFFFFF` | `#161616` | page |
| surface | `#F6F6F6` | `#1E1E1E` | sections en alternance |
| bordure | `#E5E5E5` | `#353535` | filets complets de 1 px |
| texte | `#161616` | `#FFFFFF` | corps et titres |
| texte secondaire | `#3A3A3A` | `#CECECE` | textes d'appoint |
| atténué | `#666666` | `#A6A6A6` | légendes |
| accent | `#000091` | `#8585F6` | boutons, liens, états actifs |
| survol / actif | `#1212FF` / `#2323FF` | `#A5A5FA` / `#C1C1FB` | boutons |

Le mode sombre reprend les équivalents de l'échelle du système de design de l'État (fond `#161616`, accent `#8585F6`) pour garder le respect de `prefers-color-scheme`. Les couleurs d'information (`#0063CB`, `#18753C`, `#CE0500`, `#B34000`) ne sont pas utilisées : aucun message ne dépend d'elles, et jamais de vert ou de rouge pour pour et contre.

Encodage des positions, sans jugement : pour = bleu accent plein, contre = **hachures** diagonales gris foncé (motif SVG `pattern-contre` défini une fois dans le document), abstention = gris `#929292`, non votant = gris pâle. La forme (plein, hachuré, gris) porte l'information en plus de la teinte ; la légende donne toujours libellés et effectifs. Hémicycle : points alternés bleu et gris.

### Formes

Plat : aucune ombre, aucun flou, aucun dégradé (le texte à dégradé du hero a disparu). Rayon `rounded` (4 px) pour boutons, champs, étiquettes et lignes imbriquées, `rounded-lg` (8 px) pour les cartes. Bouton principal plein bleu, bouton secondaire blanc avec filet bleu de 1 px et texte bleu, jamais en pilule. Cartes : filet complet de 1 px, titre, texte court, lien « Voir le scrutin » avec flèche.

### Mise en page

En tête : bandeau gris « Projet indépendant et non officiel · données de l'Assemblée nationale via CIVIX », puis un en tête blanc classique à filet inférieur (titre à gauche, navigation, lien « Code source » à droite), non fixe. Sections en alternance blanc et `#F6F6F6`. Grands chiffres en bleu (un chiffre, une courte légende) pour le hero et la bande de chiffres en direct. Pied de page en quatre colonnes (projet, données, informations légales, présentation) avec la ligne de licence : données sous Licence Ouverte 2.0, code sous licence MIT. Les filets d'un seul côté ne servent qu'à l'en tête et au pied de page, jamais aux cartes.

### Typographie

- **Public Sans** (OFL, USWDS) pour tout le texte et l'interface, poids 400, 500 et 700, auto hébergée via `@fontsource/public-sans`. Choisie pour sa sobriété institutionnelle proche de celle de Marianne, sans en être une copie, et parce qu'elle gère bien les chiffres tabulaires et les accents français.
- **Spectral** (OFL) pour les grands titres éditoriaux (hero, titres de section, slogan), poids 500 et 700, via `@fontsource/spectral`, comme les titres éditoriaux de data.gouv.fr.
- **Marianne n'est pas utilisée** : elle est réservée aux sites de l'État. Pas d'italique. Chiffres en Public Sans à chasse tabulaire, plus de police mono sauf pour le code et l'adresse du connecteur (système).
- Auto hébergement par `@fontsource` : aucun appel à un service de polices au chargement, ce qui sert aussi la page de confidentialité.

### Retiré

Barre de navigation flottante translucide et son menu animé, texte du titre en dégradé, révélation du slogan mot par mot (le slogan est un grand énoncé éditorial statique en Spectral), apparitions par glissement au défilement (`Reveal` supprimé), survols qui translatent ou réduisent les boutons, rotations et durées de 500 ms, mode de nombres en police mono, accent sarcelle. Restent seulement les transitions fonctionnelles (couleur en 200 ms, anneau de focus de 2 px) ; le défilement doux vers les ancres est désactivé sous `prefers-reduced-motion`.

### Limite : pas d'imitation de l'État

Aucun bloc « République Française », aucun logo Marianne, aucune bande tricolore, aucun mot « gouv » dans l'interface, aucune marque du système de design de l'État. Le bandeau « non officiel » est visible sur toutes les pages, et le pied de page répète que le projet n'est affilié ni à l'Assemblée nationale ni à CIVIX. Les seuls liens vers data.gouv.fr sont des liens vers la source des données. Le bleu `#000091` demandé est une couleur de l'identité visuelle de l'État : combiné à la mise en page, il rapproche l'aspect de celui des sites publics. Le bandeau et les mentions sont là pour que cela ne puisse pas être pris pour un site officiel ; à reconsidérer si le propriétaire préfère une teinte plus éloignée.

### Contrastes mesurés (v3)

Clair : texte 18,1 sur fond ; secondaire 11,4 ; atténué 5,74 sur fond, 5,31 sur surface, 4,86 sur survol ; accent 14,9 sur fond et 13,8 sur surface ; blanc sur bouton survolé 8,2 ; gris d'abstention 3,11 (graphique, seuil de 3 respecté) ; filet décoratif 1,26, sans rôle d'information. Sombre : texte 18,1 ; atténué 7,4 sur fond, 6,9 sur surface, 5,7 sur survol ; accent 5,8 sur fond et 5,3 sur surface ; texte foncé sur bouton 5,8 ; gris d'abstention 4,3.

## Hypothèses d'entrée (A1)

- Action principale unique : ajouter le connecteur à son assistant (bouton « Ajouter à mon assistant », cible `#installer`). Conversion : adresse copiée ou étapes d'installation ouvertes.
- Offre : gratuit, sans compte, sans clé, lecture seule, chaque réponse sourcée.
- Public : citoyens sans bagage technique, puis journalistes, enseignants, étudiants, associations civiques.
- Objections : trop technique, fiable et neutre, payant, données personnelles, compatibilité avec mon assistant.
- Preuves : uniquement des données réelles, lues en direct sur CIVIX au build puis toutes les 30 minutes. Aucun témoignage, logo, chiffre d'usage ni personne inventés.
- Trafic : réseaux sociaux, GitHub, bouche à oreille, data.gouv.fr. Les visiteurs connaissent les assistants IA, pas le mot MCP : on dit « connecteur ».
- Direction : éditorial minimal, thèmes clair et sombre selon `prefers-color-scheme`, mobile d'abord.

## Direction artistique (avant la construction)

Pas de « moderne et épuré » : ce vocabulaire produit l'allure moyenne des pages générées. Direction retenue : **journalisme de données éditorial**, en Geist.

- **Chiffres en grand.** Les nombres en direct sont le visuel : Geist Mono en `text-6xl` pour le chiffre principal, `text-4xl` pour les secondaires, légende en `text-sm` à côté.
- **Grille asymétrique.** Hero en 7 + 5 colonnes avec la conversation décalée vers le bas. Sections en 4 + 8 : le titre reste à gauche (collant sur grand écran) et le contenu occupe la colonne de droite. Rien n'est centré, sauf la barre de navigation.
- **Blanc généreux.** `py-16` à `py-24` entre sections, texte limité à 680 px, très peu de cadres.
- **Une seule couleur d'accent : un vert sarcelle profond** (`#0B6B65` en clair, `#5CC9BD` en sombre) sur base neutre plate. Justification : le sarcelle n'est lié à aucun parti, évite le bleu blanc rouge et les roses ou rouges partisans, et se distingue du bleu par défaut des pages générées. Contrastes mesurés : texte blanc sur accent 6,35 en clair, noir sur accent 10,54 en sombre.
- **Marques de données sans connotation.** Pour : accent. Contre : couleur du texte (noir ou blanc cassé). Abstention : gris moyen. Non votant : gris pâle. Pas de vert ni de rouge. Adopté et rejeté se distinguent par icône et mot.
- **Objets faits main.** Hémicycle SVG de 577 points calculé depuis les effectifs réels, courbe SVG du nombre de scrutins par jour, barres SVG, conversation construite avec un vrai scrutin. Aucune illustration de banque d'images, ni 3D, ni vidéo.

### Références et ce qu'on en retient

1. **Our World in Data** : le chiffre en tête, le graphique sobre, la source toujours sous la donnée. On reprend la source sous chaque chiffre et la sobriété des courbes.
2. **Les Décodeurs du Monde** : un fait, un graphique, une phrase claire. On reprend le ton factuel et les titres qui annoncent la conclusion.
3. **The Pudding** : une mise en page de récit avec de grandes respirations et des graphiques propres à chaque sujet. On reprend le rythme long et les objets faits main (l'hémicycle).
4. **Datawrapper Blog** : annotations discrètes et typographie qui porte le propos. On reprend les légendes en petit texte au plus près des marques.
5. **Les parlements en hémicycle (diagrammes de Wikipédia et d'Europe Elects)** : un point par siège. On reprend le principe, sans couleurs partisanes.
6. **Stripe Press et pages d'essai éditoriales** : colonne de titre à gauche, texte à droite, beaucoup de blanc. On reprend la grille 4 + 8.
7. **Linear (pages produit)** : navigation flottante, chiffres en police mono. On reprend la barre flottante floutée et l'usage de la mono pour les chiffres.
8. **Observable et Observable Plot** : série temporelle minimale, un seul trait. On reprend la courbe sans axes superflus.
9. **data.gouv.fr** : lisibilité institutionnelle, liens de source explicites. On reprend les liens vers les sources officielles, en évitant son bleu et rouge d'État.
10. **Garden de The Browser Company et pages éditoriales d'Are.na** : usage mesuré d'un seul accent. On reprend l'idée d'une seule couleur vive sur un fond plat.

## Wireframes

Les maquettes ci dessous décrivent la mise en page cible. Elles ont été écrites après une première version complète de la page et ont guidé la refonte (voir la critique plus bas).

### Hero

```
DESKTOP (12 colonnes)
+-----------------------------------------------------------------------+
|   [ MCP Assemblée nationale   liens...   GitHub  (Ajouter) ]  flottant |
|                                                                       |
|  col 1-7                                         col 8-12 (décalée)   |
|  Sachez comment ont voté vos députés,                                 |
|  source à l'appui                                 +-----------------+ |
|  sous titre (680 px max)                          | conversation    | |
|  [ Ajouter à mon assistant v ]  <- CTA unique     |  question réelle| |
|  gratuit, sans compte, sans clé                   |  réponse + barre| |
|  8 741   <- Geist Mono, text-6xl                  |  sources        | |
|  scrutins sous la 17e législature...              +-----------------+ |
|                                                   légende "illustration"|
+-----------------------------------------------------------------------+

MOBILE (une colonne)
+-------------------------+
| [MCP Assemblée   (=)]   |  pas de CTA dans la barre
| Titre (3 lignes)        |
| sous titre              |
| [ Ajouter ... v ]       |
| 8 741  (text-6xl)       |
| légende                 |
| conversation (pleine)   |
+-------------------------+
```

### Preuve en direct

```
DESKTOP
+-----------------------------------------------------------------------+
| En direct (titre pleine largeur, intro)                               |
| 412            |  64 scrutins cette semaine | 577 députés             |
| scrutins/30 j  |  X adoptés, Y rejetés      | 12 groupes              |
| ~~~ courbe SVG |                            |                         |
|-----------------------------------------------------------------------|
| Cette semaine : cartes par dossier (2 colonnes), lignes de scrutin    |
| Tendances : [barres par jour] [dossiers 7/30 j] [adoption] [finals]   |
| Composition : hémicycle (col 1-7)        | liste des groupes (col 8-12)|
+-----------------------------------------------------------------------+
MOBILE : chiffres empilés, cartes en une colonne, hémicycle pleine largeur
         puis liste des groupes dessous.
```

### Démo

```
DESKTOP (2 + 3)                      MOBILE
+-----------+--------------------+   +----------------+
| Député    | résultats          |   | Député (champ) |
| [champ v] | (squelette puis    |   | suggestions    |
| suggestions| liste de scrutins)|   | Sujet (champ)  |
| Sujet     |                    |   | [Voir les votes]|
| [Voir...] |                    |   | résultats      |
+-----------+--------------------+   +----------------+
```

### Installation

```
DESKTOP (4 + 8)                         MOBILE
+-----------+-------------------------+ +----------------------+
| titre     | Étape 1 [adresse][Copier]| | titre                |
| (collant) | Étape 2 [Claude|ChatGPT|| | Étape 1 adresse+Copier|
|           |  Gemini|En local]        | | Étape 2 onglets      |
|           |  étapes numérotées       | | étapes, note         |
|           | Étape 3 demander         | | Étape 3              |
+-----------+-------------------------+ +----------------------+
```

### Révélation du slogan

```
+-----------------------------------------------------------------------+
|  Les chiffres viennent de l'Assemblée. Les liens mènent à la source.  |
|  Le jugement vous appartient.      (text-4xl à text-5xl, 680 px max)  |
|  chaque mot passe de 30 % à 100 % en croisant la ligne à 60 % de l'écran |
+-----------------------------------------------------------------------+
```

### FAQ

```
DESKTOP (4 + 8)                        MOBILE
+-----------+------------------------+ +---------------------+
| titre     | > question 1           | | titre               |
| (collant) | > question 2 ...       | | > question 1 ...    |
+-----------+------------------------+ +---------------------+
```

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
- Marques de données (barres, points de légende) : dessinées en SVG avec `fill`, hors des fonds de surface. Couleurs de position non connotées (accent sarcelle, couleur du texte, gris), jamais vert ou rouge. Adopté et rejeté sont distingués par une icône et un mot, pas par une couleur.
- Mouvement : courbe `cubic-bezier(0.22, 1, 0.36, 1)` exposée comme jeton `ease-weighted` et appliquée par défaut à toutes les transitions, `duration-500` pour les positions, `duration-300` pour les couleurs. Seulement `transform` et `opacity`. `prefers-reduced-motion` remplace les déplacements par un simple fondu. Révélations avec `IntersectionObserver`, une seule fois.
- Navigation : barre flottante centrée, translucide avec flou, icône de menu animée, panneau mobile pleine hauteur, liens qui entrent à 60 ms d'intervalle (plafond 400 ms), page courante indiquée.

## 10. Données en direct et appels CIVIX

Voir `README.md` pour la liste des appels par rendu et les durées de cache.

## Résultat de la checklist

Vérifié par grep sur `src/` et par lecture. Pass sauf mention.

Stratégie
- Une offre, un public, une action : pass (CTA « Ajouter à mon assistant », cible `#installer`)
- Pas de CTA concurrent au dessus de la ligne de flottaison : pass (le CTA de la barre est masqué sous `lg` via `max-lg:hidden`, GitHub en icône discrète)
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
- Fonds sombres limités à la liste : pass pour les surfaces (`#131209`, `#181818`, `#1F1F1F`, `#272727`, `#313131`) ; les marques de données SVG (sarcelle, texte, gris) sont des remplissages hors surface

Contenu et finitions
- Vraie copie, aucun mot interdit : pass (aucune personne, citation, logo ni statistique inventés)
- États survol, actif, focus, chargement, vide, erreur : pass (squelettes de la démo, états vides et erreurs composés, repli « Données momentanément indisponibles »)
- Pas de lien mort, page courante indiquée : pass (suivi de section dans la barre, `aria-current`)
- 404, mentions légales, confidentialité, validation de formulaire, favicon, balises meta, textes alternatifs : pass (`not-found.tsx`, `/mentions`, `/confidentialite`, validation du formulaire de démo, `icon.svg`, OG dynamique)

Non vérifié : rendu visuel clair et sombre sur tous les écrans, lecteur d'écran, Lighthouse. Un contrôle visuel mobile du hero a été fait dans Chrome.


## Critique de la première version

Question posée : qu'est ce qui rend cette page générique, et qu'est ce qui la rendrait distinctive ?

Constats sur la première version complète :
1. Tout était centré ou empilé en grilles de cartes identiques, avec des titres de section au dessus. C'est la mise en page par défaut des pages générées.
2. L'accent était un bleu franc, couleur par défaut des pages générées et proche des codes d'un drapeau.
3. Les chiffres en direct étaient de petites étiquettes ; la composition des groupes était une liste de barres grises ; les tendances n'avaient pas de forme propre.

Corrections appliquées (les trois premières) :
1. **Grille asymétrique** : hero 7 + 5 avec conversation décalée, sections en 4 + 8 avec titre collant, étapes d'installation et « comment ça marche » en liste verticale à gros chiffres.
2. **Accent unique sarcelle**, marques de données ramenées à l'accent, au texte et au gris.
3. **Objets de données** : chiffres en Geist Mono `text-6xl`, bande de chiffres en tête de la preuve en direct avec courbe SVG, hémicycle SVG de 577 points avec liste interactive.

Reste à faire (non traité) : une version annotée des barres par jour (pic nommé), un état « chargement » pour les chiffres du hero, et un contrôle sur de vrais téléphones.

## Audit d'accessibilité

Contrastes mesurés avec la formule WCAG sur les jetons réels :
- Clair : texte `#111111` sur fond 18,9 ; gris secondaire `#5C5C57` sur fond 6,7, sur surface 6,2, sur survol 5,7 ; blanc sur accent 6,35.
- Sombre : texte `#F4F4F1` sur fond 17,0 ; gris secondaire `#A6A6A0` sur fond 7,7, sur surface 7,3, sur survol 6,1 ; noir sur accent 10,5.
- Marques graphiques : gris d'abstention 3,5 sur fond clair et 5,4 sur fond sombre (seuil de 3 pour les graphiques) ; l'information n'est jamais portée par la couleur seule (légende avec libellés et effectifs).
- Focus : contour de 2 px couleur accent, décalé de 2 px, sur tous les éléments focalisables. Ordre de tabulation : lien d'évitement, barre, contenu dans l'ordre du document, pied de page.
- Étiquettes : champs de la démo et des filtres associés à un `label`, erreurs reliées par `aria-describedby`, `aria-invalid`, combobox avec `aria-expanded` et navigation au clavier.
- Graphiques : chaque SVG porte `role="img"` et un `aria-label` chiffré ; l'hémicycle est doublé par une liste textuelle de boutons avec effectifs ; la courbe a des `title` par jour.
- Mouvement : `prefers-reduced-motion` retire les déplacements, le slogan s'affiche sans transition d'attente.
- Limites : pas de test avec lecteur d'écran réel ; l'hémicycle en survol n'a pas d'équivalent tactile autre que le bouton de la liste.

## Passage mobile

Contrôle dans Chrome à la plus petite largeur permise par l'outil (500 px) : aucun débordement horizontal (`scrollWidth` égal à `innerWidth`), titre en trois lignes, CTA et chiffre visibles sans défiler, conversation en pleine largeur. Un défaut trouvé et corrigé : le CTA de la barre se superposait au bouton de menu (la classe `hidden` perdait contre `inline-flex`), remplacé par `max-lg:hidden`. Le rendu à 375 px n'a pas pu être testé directement : à vérifier sur un vrai téléphone.

## Pourquoi ces choix de mise en page

- Hero 7 + 5 : le texte garde sa mesure de lecture, la conversation réelle sert de preuve juste à côté du CTA, et son décalage vers le bas casse l'alignement en deux blocs égaux.
- Titres en colonne gauche collante : sur un récit long, le titre reste visible pendant la lecture du contenu, ce qui remplace les en têtes centrés répétés.
- Le chiffre avant l'explication : le public sceptique croit d'abord ce qu'il peut vérifier.
- Hémicycle plutôt que barres : c'est la forme que le public reconnaît pour une assemblée, et un point par siège rend le total (577) tangible.


## Checklist après la révision v3

Les règles visuelles de la skill (police unique Geist, fonds sombres, dégradé du titre, mouvement, navigation flottante, révélation du slogan) sont volontairement écartées par la consigne du propriétaire. Contrôles qui restent valables :
- Une action principale, pas de CTA concurrent : pass (aucun bouton dans l'en tête, un seul CTA par zone, bouton secondaire seulement ailleurs)
- Échelle de texte Tailwind, espacements de la table, aucune valeur arbitraire `-[` : pass (greps ci dessous)
- Aucun dégradé, flou, ombre, `bg-clip-text` : pass (grep)
- Pas d'italique, poids 400, 500 et 700 seulement : pass
- Pas de trait d'union dans les textes, pas de mot orphelin : pass avec les réserves précédentes
- Écarts de bordure : filets d'un seul côté seulement dans l'en tête et le pied de page
- États survol, actif (couleur), focus, chargement, vide, erreur : pass
- Non imitation de l'État : pass (voir la limite ci dessus)
Non vérifié : lecteur d'écran, Lighthouse, rendu sur un vrai téléphone.
