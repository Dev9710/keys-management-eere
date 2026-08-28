---
name: Portail EERE — Gestion des clés
description: Le registre vivant des clés de l'église — vert profond, sérif de titre, tableaux tenus avec soin.
colors:
  teal-esperance: "#3a9f87"
  teal-esperance-dark: "#2a7562"
  teal-esperance-light: "#edf7f5"
  vert-cantique-deep: "#0d3028"
  vert-cantique-mid: "#1a5040"
  orange-registre: "#FFA500"
  orange-registre-dark: "#e8920a"
  orange-registre-gros-texte: "#cc8400"
  orange-registre-lisible: "#a36900"
  rouge-retrait: "#dc2626"
  rouge-retrait-dark: "#b91c1c"
  bg-page: "#f8fafc"
  bg-surface: "#ffffff"
  bg-surface-tinted: "#f8fffe"
  bg-warning: "#fffbeb"
  bg-danger: "#fef2f2"
  border-soft: "#e8f0ed"
  border-neutral: "#e2e8f0"
  text-primary: "#0f172a"
  text-secondary: "#64748b"
  text-tertiary: "#94a3b8"
typography:
  display:
    fontFamily: "DM Serif Display, Georgia, serif"
    fontSize: "1.4rem"
    fontWeight: 400
    lineHeight: 1.2
  headline:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    lineHeight: 1.3
  title:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "0.88rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "0.68rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.08em"
  caption:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
  metric:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "2.2rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
rounded:
  xs: "2px"
  sm: "8px"
  md: "9px"
  lg: "10px"
  xl: "12px"
  xxl: "14px"
  pill: "50px"
  circle: "50%"
spacing:
  xs: "0.35rem"
  sm: "0.6rem"
  md: "1rem"
  lg: "1.25rem"
  xl: "2rem"
components:
  button-add:
    backgroundColor: "{colors.orange-registre}"
    textColor: "{colors.bg-surface}"
    rounded: "{rounded.lg}"
    padding: "0.6rem 1.2rem"
    typography: "{typography.body}"
  button-add-hover:
    backgroundColor: "{colors.orange-registre-dark}"
    textColor: "{colors.bg-surface}"
  button-primary:
    backgroundColor: "{colors.teal-esperance}"
    textColor: "{colors.bg-surface}"
    rounded: "{rounded.md}"
    padding: "0.6rem 1.2rem"
    typography: "{typography.body}"
  button-primary-hover:
    backgroundColor: "{colors.teal-esperance-dark}"
    textColor: "{colors.bg-surface}"
  button-danger:
    backgroundColor: "{colors.rouge-retrait}"
    textColor: "{colors.bg-surface}"
    rounded: "{rounded.md}"
    padding: "0.6rem 1.2rem"
  button-danger-hover:
    backgroundColor: "{colors.rouge-retrait-dark}"
    textColor: "{colors.bg-surface}"
  button-cancel:
    backgroundColor: "{colors.bg-surface}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: "0.6rem 1.2rem"
  input-field:
    backgroundColor: "{colors.bg-surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "0.55rem 1rem"
    typography: "{typography.body}"
  table-header:
    backgroundColor: "{colors.teal-esperance}"
    textColor: "{colors.bg-surface}"
    padding: "0.75rem 1rem"
    typography: "{typography.label}"
  card-surface:
    backgroundColor: "{colors.bg-surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.xl}"
    padding: "1rem 1.25rem"
  page-banner:
    backgroundColor: "{colors.vert-cantique-deep}"
    textColor: "{colors.bg-surface}"
    rounded: "{rounded.xl}"
    padding: "1rem 1.5rem"
---

# Design System: Portail EERE — Gestion des clés

## Overview

**Creative North Star: « Le Registre de la Sacristie »**

Un grand livre tenu avec soin. Le portail hérite de la tenue d'un registre paroissial : une reliure
vert profond en tête de page, une écriture de titre en sérif, et en dessous des colonnes ordonnées
où chaque clé, chaque exemplaire, chaque détenteur occupe sa ligne. La rigueur vient de la table ;
la chaleur vient du vert et de la sérif. Rien n'y est décoratif au sens gratuit : le bandeau vert
n'est pas un hero marketing, c'est la couverture du registre qu'on ouvre.

L'humeur est **calme, ordonnée, chaleureuse**. Le vert profond apaise, la structure rassure, la
sérif humanise un outil qui pourrait n'être qu'une grille. La densité est réelle — 148 types de
clés, 890 exemplaires — mais elle est tenue par la hiérarchie plutôt que par la compression :
en-têtes de colonne en capitales espacées, lignes alternées, liseré teal au survol pour ne jamais
perdre la ligne qu'on suit du doigt sur un écran de 1366 px.

Le système est **cohérent mais pas encore centralisé** : `base.html` ne définit que trois variables
CSS ; chaque page redéclare son propre bloc `:root`. Ce document est la source de vérité en
attendant une centralisation. Les valeurs du frontmatter sont normatives — c'est vers elles qu'il
faut converger, pas vers ce qu'une page a copié.

**Key Characteristics:**
- Bandeau au gradient vert en tête de chaque page, coins 12 px, titre sérif blanc
- Tableaux à en-tête teal plein, capitales espacées, lignes alternées blanc / blanc-vert
- Une seule couleur d'appel — l'orange — réservée à l'ajout
- Arrondis doux et généreux (9-12 px), cibles de clic larges
- Surfaces légèrement soulevées, jamais collées au fond
- Zéro dépendance de build : CSS écrit à la main dans chaque page

## Colors

Une palette de registre : un vert unique décliné du sombre au très clair, une seule couleur d'appel
orange, un rouge strictement réservé au retrait, et des neutres froids qui laissent le vert parler.

### Primary

- **Teal Espérance** (`#3a9f87`) : la couleur de l'application. En-têtes de tableau pleins, boutons
  de modification et d'enregistrement, liseré gauche au survol des lignes, anneau de focus des
  champs. C'est le vert qui dit « ceci est le portail ».
- **Teal Espérance sombre** (`#2a7562`) : survol de tous les boutons teal, et texte sur fond teal
  très clair (messages d'attribution).
- **Teal Espérance clair** (`#edf7f5`) : survol léger des lignes de tableau, fonds de badge, fond
  des messages d'information.

### Secondary

- **Vert Cantique profond** (`#0d3028`) et **Vert Cantique médian** (`#1a5040`) : le gradient
  signature `linear-gradient(135deg, …)`. Réservé aux bandeaux de page, aux en-têtes de modale et
  au hero d'accueil. C'est la reliure du registre — jamais un fond de contenu.

### Tertiary

- **Orange Registre gros texte** (`#cc8400`) : le ton le plus clair de la rampe qui tienne
  encore sur blanc — 3,06:1, pour 3:1 requis. Valable **uniquement** au-delà de 24 px, ou de
  18,7 px en gras. La marche suivante (`#d18a00`) échoue à 2,86:1.
- **Orange Registre lisible** (`#a36900`) : le ton à employer dès que l'orange porte du texte
  courant sur surface claire — 4,59:1, au-dessus d'AA. `#FFA500` n'y tient que 1,97:1 et
  `#e8920a` 2,46:1. Les aplats et liserés, eux, gardent `#FFA500`.
- **Orange Registre** (`#FFA500`) : la seule couleur d'appel. Bouton « Ajouter », accent des lignes
  en incohérence. Survol **Orange Registre sombre** (`#e8920a`).
- **Rouge Retrait** (`#dc2626`) : suppression et danger uniquement. Survol `#b91c1c`, fonds
  `#fef2f2` / `#fee2e2`.

### Neutral

- **Fond page** (`#f8fafc`) : le papier du registre, derrière toutes les surfaces.
- **Surface** (`#ffffff`) : cartes, panneaux de filtre, corps de modale, lignes impaires.
- **Surface teintée** (`#f8fffe`) : lignes paires des tableaux, pieds de modale, survol de carte.
  Un blanc à peine verdi qui rythme la lecture sans introduire de gris.
- **Bordure douce** (`#e8f0ed`) : contours de carte et de panneau — verdie, jamais neutre.
- **Bordure neutre** (`#e2e8f0`) : contours de champ et de bouton secondaire.
- **Texte principal** (`#0f172a`), **secondaire** (`#64748b`), **tertiaire** (`#94a3b8`) : contenu,
  légendes, labels en capitales.

### Named Rules

**La Règle de l'Unique Orange.** L'orange ne signifie qu'une chose : *ajouter*. Un second usage
décoratif de l'orange dissout le seul repère d'action de l'interface. Test : sur n'importe quelle
page, comptez les éléments orange — s'il y en a plus d'un par zone, il y en a un de trop.

**La Règle de la Reliure.** Le gradient Vert Cantique n'habille que ce qui *ouvre* une vue :
bandeau de page, en-tête de modale. Jamais une carte, jamais une ligne, jamais un bouton.

**La Règle du Rouge Rare.** Le rouge est le vocabulaire du retrait — supprimer, retirer une clé,
signaler une erreur bloquante. Il ne sert jamais à attirer l'attention sur autre chose.

## Typography

**Display Font:** DM Serif Display (fallback Georgia, serif)
**Body Font:** DM Sans — 400 / 500 / 600 / 700 (fallback sans-serif)
**Icônes:** FontAwesome 6.4 (`fas fa-…`)

**Character:** Une sérif de titre chaleureuse posée sur une grotesque neutre et très lisible. La
sérif ne sert qu'aux titres — c'est la main qui a écrit sur la couverture ; DM Sans porte tout le
reste, y compris les chiffres du parc, où sa lisibilité en petit corps compte plus que son style.

### Hierarchy

- **Display** (DM Serif Display, 400, 1.4rem) : titre du bandeau de page, titre de modale. Toujours
  en blanc sur le gradient.
- **Headline** (DM Sans, 700, 1.15rem) : titres de section et de carte à l'intérieur du contenu.
- **Title** (DM Sans, 600, 0.9rem) : intitulés de champ, en-têtes de bloc, noms de clé en évidence.
- **Body** (DM Sans, 400, 0.88rem) : le corps de l'application — cellules de tableau, textes, aides.
  C'est la taille de référence du portail, calibrée pour la densité sur 1366 px.
- **Label** (DM Sans, 700, 0.68rem, `letter-spacing: .08em`, capitales) : labels de filtre.
- **Caption** (DM Sans, 400, 0.75rem) : précisions tertiaires sous un chiffre ou un intitulé —
  ce qui explique sans jamais porter la donnée elle-même.
- **Metric** (DM Sans, 700, 2.2rem, `letter-spacing: -0.02em`, `line-height: 1`) : les chiffres
  d'état du parc, et eux seuls. C'est la seule échappée hors de l'échelle courante ; elle se paie
  par sa rareté — une occurrence par page, sur le bandeau de chiffres.
- **En-tête de tableau** (DM Sans, 700, 0.75rem, `letter-spacing: .06em`, capitales) : la variante
  du label sur fond teal plein, en capitales.

### Named Rules

**La Règle de la Sérif Rare.** DM Serif Display n'apparaît que sur le gradient vert : titre de page,
titre de modale. Une sérif dans un tableau ou un bouton casse la lecture et l'identité d'un coup.

**La Règle du Corps Unique.** `0.88rem` est le corps de l'application. Descendre en dessous
(`0.78rem`, `0.75rem`) est réservé aux labels et métadonnées, jamais à une donnée que l'utilisateur
doit lire pour décider.

## Layout

Pleine largeur, pas de conteneur centré étroit : chaque page occupe la largeur disponible avec un
padding de `1.25rem 2rem 1.5rem` sur fond `#f8fafc`. La structure verticale est toujours la même —
**bandeau vert → panneau de filtres → contenu (tableau ou cartes)**, séparés par `1rem`.

Le panneau de filtres est une carte blanche en flex, `gap: 1.25rem`, chaque groupe à `min-width:
220px` et `flex: 1` : il se réorganise seul quand la largeur manque, sans media query.

Rythme d'espacement : `0.35rem` (entre label et champ), `0.6rem` / `1rem` (padding interne),
`1.25rem` (gouttière entre blocs), `2rem` (marge latérale de page).

Ruptures observées : `768px` (principale), puis `480px`, `640px`, `992px`, `1024px`. Une règle
`@media print` existe pour les exports papier, et `prefers-reduced-motion: reduce` est respecté.

**Cible d'écran réelle : ~1366 px.** Aucun tableau ne doit déborder horizontalement à cette
largeur ; les tableaux longs se gèrent par en-tête collant et pagination, pas par défilement
latéral.

### Named Rules

**La Règle des Trois Bandes.** Bandeau, filtres, contenu — dans cet ordre, sur toute page de
gestion. Un utilisateur qui change d'écran doit retrouver ses repères au même endroit.

## Elevation & Depth

Le système est **légèrement soulevé en permanence** : cartes et panneaux portent une ombre douce
constante (`0 1px 3px rgba(0,0,0,.04)`, ou `0 4px 16px rgba(0,0,0,.06), 0 1px 3px rgba(0,0,0,.04)`
pour les blocs principaux) qui les détache du fond `#f8fafc` sans jamais les faire flotter. La
profondeur se lit d'abord à cette ombre, ensuite aux fonds teintés.

L'interaction ajoute de la lumière colorée plutôt que de l'ombre noire : un bouton survolé projette
une lueur de sa propre couleur, un champ focalisé s'entoure d'un anneau teal.

### Shadow Vocabulary

- **Repos carte** (`box-shadow: 0 1px 3px rgba(0,0,0,.04)`) : panneaux de filtre, cartes de liste.
- **Repos bloc** (`box-shadow: 0 4px 16px rgba(0,0,0,.06), 0 1px 3px rgba(0,0,0,.04)`) : conteneurs
  principaux, tableau.
- **Anneau de focus** (`box-shadow: 0 0 0 3px rgba(58,159,135,.12)`) : tout champ focalisé. Version
  renforcée `.25` sur les contrôles critiques.
- **Lueur d'ajout** (`box-shadow: 0 4px 14px rgba(255,165,0,.35)`) : survol du bouton Ajouter.
- **Lueur de retrait** (`box-shadow: 0 4px 12px rgba(220,38,38,.25)`) : survol des actions de
  suppression.
- **Barre de navigation** (`box-shadow: 0 2px 10px rgba(0,0,0,.1)`) : l'ombre portée de l'en-tête
  collant, sur les 19 pages. Elle n'appartient qu'à lui.
- **Modale** (`box-shadow: 0 20px 60px rgba(0,0,0,.2)`) : la seule ombre franche du système ; elle
  marque la rupture de plan.

### Named Rules

**La Règle de l'Ombre Colorée.** Au survol, l'ombre porte la couleur du bouton, jamais du noir. Le
noir est réservé au repos et aux modales.

**La Règle de l'Anneau Teal.** Tout focus clavier se signale par l'anneau teal 3 px. Il ne se
supprime jamais : c'est le seul repère de navigation au clavier du portail.

## Shapes

Un vocabulaire arrondi **doux et généreux**, cohérent avec un public peu à l'aise : les cibles sont
larges et les angles jamais coupants.

- `2px` : micro-éléments, liserés.
- `8px` : petits badges, puces.
- `9px` : champs de formulaire, selects, boutons secondaires — le rayon le plus fréquent (34×).
- `10px` : boutons d'action principaux, messages, coins hauts des tableaux
  (`border-radius: 10px 0 0 0` / `0 10px 0 0`).
- `12px` : bandeaux de page, cartes, panneaux de filtre.
- `14px` : modales — le rayon le plus grand, réservé au plan qui recouvre.
- `50px` : pilules et badges de statut.
- `50%` : pastilles d'icône et avatars.

Bordures : `1px solid` pour les surfaces, `1.5px solid` pour les champs de saisie — le champ est
volontairement plus dessiné que la carte, parce que c'est là qu'on agit.

### Named Rules

**La Règle de l'Échelle Fermée.** Les rayons du système sont 2 / 8 / 9 / 10 / 12 / 14 / 50 px et
50 %. Une nouvelle valeur intermédiaire (11 px, 13 px) n'est jamais justifiée.

## Components

### Buttons

- **Shape:** arrondis doux — 10 px pour les actions principales, 9 px pour les secondaires.
- **Ajouter:** fond Orange Registre (`#FFA500`), texte blanc, `padding: .6rem 1.2rem`, DM Sans 600
  à `0.88rem`, icône FontAwesome à gauche, `gap: 7px`.
- **Modifier / Enregistrer:** fond Teal Espérance (`#3a9f87`), texte blanc, mêmes métriques.
- **Supprimer:** fond Rouge Retrait (`#dc2626`), texte blanc.
- **Annuler:** fond blanc, bordure `#e2e8f0`, texte `#64748b`.
- **Hover:** passage à la variante sombre + lueur colorée + `transform: translateY(-1px)`.
- **Active:** `transform: scale(.98)`.
- **Disabled:** fond `rgba(255,255,255,.16)`, texte `rgba(255,255,255,.55)`, `cursor: not-allowed`.
- **Transition:** `background .2s, box-shadow .2s, transform .1s`.

### Inputs / Fields

- **Style:** fond blanc, bordure `1.5px solid #e2e8f0`, rayon 9 px, `padding: .55rem 1rem`, DM Sans
  `0.88rem`, `outline: none`.
- **Label:** au-dessus, `0.68rem`, 700, capitales, `letter-spacing: .08em`, couleur `#94a3b8`,
  `gap: .35rem`.
- **Focus:** bordure Teal Espérance + anneau `0 0 0 3px rgba(58,159,135,.12)`.
- **Transition:** `border-color .2s, box-shadow .2s`.
- **Error:** bordure `1px solid rgba(220,38,38,.2)`, fond `#fef2f2`, texte `#b91c1c`.

### Tables

Le composant central du portail — c'est là que vit le registre.

- **En-tête:** fond Teal Espérance plein, texte blanc, `0.75rem` 700 capitales,
  `letter-spacing: .06em`, `padding: .75rem 1rem`, aligné à gauche, sans bordure ; coins hauts
  arrondis 10 px sur la première et la dernière colonne.
- **Lignes:** alternance `#ffffff` / `#f8fffe`, séparateur `1px solid #f1f5f4`.
- **Survol:** fond `#edf7f5` + liseré gauche teal — le repère de ligne, indispensable à cette
  densité.
- **Ligne en incohérence:** fond `#fffbeb`, liseré gauche orange. C'est l'écart entre le théorique
  et le réel qui se signale, jamais une erreur de l'utilisateur.
- **Colonnes numériques** (quantités, armoire, coffre) : centrées ; colonne de sélection à 5 %.
- **Transition de ligne:** `background .15s, border-left-color .15s`.

### Cards / Containers

- **Corner Style:** 12 px.
- **Background:** blanc ; survol `#f8fffe`.
- **Border:** `1px solid #e8f0ed`.
- **Shadow:** repos carte (voir Elevation & Depth).
- **Internal Padding:** `1rem 1.25rem`.
- **Survol:** liseré gauche teal, comme les lignes de tableau — même grammaire.

### Modals

- **Corner Style:** 14 px.
- **En-tête:** gradient Vert Cantique, titre DM Serif Display blanc.
- **Corps:** blanc. **Pied:** `#f8fffe`, avec Annuler à gauche et l'action teal à droite.
- **Shadow:** `0 20px 60px rgba(0,0,0,.2)`.

### Navigation

Barre fixe en haut (`z-index: 1000`), logo texte « EERE » à 24 px gras à gauche, liens en flex avec
`gap: 30px`. Liens en Teal Espérance, 500 ; au survol passage à `#2a7562` et **soulignement animé**
qui se déploie de la gauche (`transform: scaleX(0) → scaleX(1)`, `.3s`). L'onglet actif reste en 700
avec son soulignement déployé en permanence.

**Les entrées interdites à un rôle sont absentes du menu, jamais grisées.**

### Page Banner (composant signature)

La reliure du registre : bandeau pleine largeur au gradient Vert Cantique, rayon 12 px,
`padding: 1rem 1.5rem`, en flex avec `gap: 1.25rem` et `flex-wrap: wrap`. Il contient le titre sérif
blanc, un sous-titre à `rgba(255,255,255,.65)` en `0.82rem`, puis — poussés à droite par
`margin-left: auto` — le bouton Ajouter, la recherche et le compteur d'éléments. C'est le seul
endroit où l'orange côtoie le gradient.

## Do's and Don'ts

### Do:

- **Do** ouvrir chaque page de gestion par le bandeau au gradient Vert Cantique, coins 12 px, titre
  DM Serif Display blanc — c'est le repère d'orientation du portail.
- **Do** réserver l'orange (`#FFA500`) à l'action d'ajout, une occurrence par zone.
- **Do** garder l'alternance `#ffffff` / `#f8fffe` et le liseré teal au survol sur tout tableau : à
  890 exemplaires, c'est ce qui empêche de perdre sa ligne.
- **Do** signaler les incohérences de stock par le fond `#fffbeb` et le liseré orange, jamais par du
  rouge : un écart n'est pas une faute.
- **Do** conserver l'anneau de focus teal (`0 0 0 3px rgba(58,159,135,.12)`) sur tous les champs.
- **Do** rester dans l'échelle de rayons 2 / 8 / 9 / 10 / 12 / 14 / 50 px.
- **Do** écrire le CSS à la main dans la page, en réutilisant le bloc `:root` déjà présent.
- **Do** masquer les entrées de menu interdites à un rôle plutôt que les griser.
- **Do** vérifier chaque écran à 1366 px de large avant de le considérer terminé.

### Don't:

- **Don't** ressembler à un SaaS générique : pas de bleu-violet, pas de dégradés décoratifs hors
  gradient signature, pas d'illustration 3D, pas de hero marketing. Le portail est adopté, il n'est
  pas à vendre.
- **Don't** retomber dans le back-office brut : ni admin Django nu, ni Bootstrap par défaut, ni
  tableau gris sans hiérarchie.
- **Don't** livrer un tableur déguisé : une grille sans bandeau, sans alternance de lignes et sans
  repère de survol n'est pas une page du portail.
- **Don't** utiliser DM Serif Display ailleurs que sur le gradient vert.
- **Don't** poser le gradient Vert Cantique sur une carte, une ligne ou un bouton.
- **Don't** employer le rouge pour attirer l'attention sur autre chose qu'une suppression ou une
  erreur bloquante.
- **Don't** introduire un rayon hors échelle, ni une ombre noire au survol (l'ombre de survol porte
  la couleur du bouton).
- **Don't** vendre : bannir « gérez sereinement », « gagnez du temps », « notre application ». Dire
  où l'on est, ce qu'on peut faire, comment procéder.
- **Don't** ajouter une dépendance de build, un framework JS ou un bundler.
