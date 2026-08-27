# Design System — Portail EERE

Référence visuelle du portail de gestion des clés de l'Église Évangélique Rencontre Espérance.
**À lire avant toute nouvelle page ou tout composant**, pour que l'ensemble reste cohérent.

> Stack : Django + templates HTML, CSS écrit à la main dans chaque page, FontAwesome 6, Google Fonts.
> Les 19 pages étendent [`listings/templates/listings/base.html`](merchex/listings/templates/listings/base.html).

---

## État actuel (à savoir)

Le système est **cohérent mais pas encore centralisé** : `base.html` ne définit que 3 variables CSS
(`--primary-color`, `--primary-hover`, `--accent-color`). Le reste de la palette est **répété en
dur** dans chaque page (`#3a9f87` apparaît ~38×, `#0d3028` ~49×…). Ce document sert de source de
vérité en attendant une éventuelle centralisation des tokens dans `base.html`.

---

## Palette

### Vert teal — primaire
| Rôle | Hex |
|---|---|
| Primaire (`--primary-color`) | `#3a9f87` |
| Primaire survol (`--primary-hover`) | `#2a7562` |
| Fond teal très clair (survol léger, badges) | `#edf7f5` |
| Fond blanc-vert (lignes paires) | `#f8fffe` |

### Gradient signature (en-têtes, hero, modals)
```css
background: linear-gradient(135deg, #0d3028 0%, #1a5040 100%);
```

### Orange — accent / action « Ajouter »
| Rôle | Hex |
|---|---|
| Accent (`--accent-color`) | `#FFA500` |
| Orange survol / warning | `#e8920a` |
| Fond warning clair | `#fffbeb` |

### Rouge — danger / suppression
| Rôle | Hex |
|---|---|
| Danger | `#dc2626` |
| Danger survol | `#b91c1c` |
| Fond danger clair | `#fef2f2` / `#fee2e2` |

### Neutres (slate)
| Rôle | Hex |
|---|---|
| Fond page | `#f8fafc` |
| Blanc surfaces | `#ffffff` |
| Texte principal | `#0f172a` |
| Texte secondaire | `#64748b` |
| Bordure | `#e2e8f0` |

---

## Typographie

Chargées via Google Fonts dans `base.html` :

| Police | Usage |
|---|---|
| **DM Serif Display** | Titres de page, titres de modals, hero |
| **DM Sans** (400/500/600/700) | Corps, labels, boutons, tableaux |

```css
font-family: 'DM Serif Display', serif;   /* titres */
font-family: 'DM Sans', sans-serif;        /* tout le reste */
```

Icônes : **FontAwesome 6.4** (`fas fa-…`).

---

## Composants

### En-tête de page (bandeau vert)
Gradient signature, coins arrondis 12 px, titre en DM Serif Display blanc, contient le bouton
Ajouter, la recherche et un compteur.

### Boutons
| Bouton | Fond | Survol | Texte |
|---|---|---|---|
| Ajouter | `#FFA500` | `#e8920a` | blanc |
| Modifier | `#3a9f87` | `#2a7562` | blanc |
| Supprimer | `#dc2626` | `#b91c1c` | blanc |
| Enregistrer (modal) | `#3a9f87` | `#2a7562` | blanc |
| Annuler (modal) | blanc, bordure `#e2e8f0` | — | `#64748b` |

### Tableaux
En-tête teal `#3a9f87` texte blanc, majuscules espacées. Lignes alternées `#ffffff` / `#f8fffe`,
survol `#edf7f5` avec liseré gauche teal. Lignes en incohérence : fond `#fffbeb`, liseré orange.

### Modals
`.modal-content` : coins 14 px, ombre portée. En-tête au gradient signature, titre DM Serif Display
blanc. Corps blanc, pied `#f8fffe`.

### Cartes / listes
Fond blanc, coins 12 px, bordure `#e8f0ed`, ombre douce. Survol : fond `#f8fffe`, liseré gauche teal.

### Messages (voir `MESSAGE_TAGS` dans settings)
Les gabarits écrivent `class="alert-{{ message.tags }}"` ; `MESSAGE_TAGS` fournit `danger` / `success`
/ `warning` / `info` (**sans** préfixe `alert-`). Danger : fond `#fef2f2`, bordure `#fca5a5`, liseré
gauche 4 px `#dc2626`, texte `#b91c1c`.

---

## Rayons de bordure

Échelle observée : `8px` (petits éléments), `9–10px` (champs, boutons), `12–14px` (cartes, modals),
`50px` (pilules, badges arrondis). S'y tenir plutôt que d'inventer de nouvelles valeurs.

---

## Ton éditorial

Le portail est **déjà adopté, il n'est pas à vendre**. Tous les textes (titres, sous-titres,
boutons, messages, aides, erreurs) adoptent une posture d'**accompagnement** : renseigner, guider,
orienter l'utilisateur — jamais un argumentaire commercial. Bannir « gérez sereinement », « gagnez
du temps », « notre application ». Préférer dire *où l'on est*, *ce qu'on peut faire*, *comment
procéder*. Ton chaleureux mais sobre.

---

## Pages de référence (design appliqué)

- `listings/templates/listings/keys.html` — gestion des clés
- `listings/templates/listings/teams.html` — gestion des équipes
- `listings/templates/listings/attribute.html` — attribution des clés
- `listings/templates/listings/home.html` — accueil (hero + modules)
