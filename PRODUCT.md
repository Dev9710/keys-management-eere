# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Utilisateurs internes de l'Église Évangélique Rencontre Espérance, authentifiés, travaillant
**principalement depuis un poste fixe** (bureau de l'église). Le mobile existe mais reste marginal.

**Public non technique, peu à l'aise avec l'informatique.** Ce sont des bénévoles adultes, pas des
opérateurs formés : libellés explicites, confirmations claires, aucun jargon technique, aucune
mécanique qui suppose de connaître le modèle de données.

**Saisie assurée par 2-3 gestionnaires** qui se partagent le travail — la concurrence de saisie est
donc un cas réel, pas théorique : deux personnes peuvent toucher la même clé le même jour.

### Les trois rôles (modèle `Owner`, champ `role`)

| Rôle | Peut | Ne peut pas |
|---|---|---|
| **Administrateur** (`admin`) | Tout : clés, attributions, équipes, membres, **création de comptes**, **historique des actions** (création, modification, lecture, suppression), **synthèse globale + statistiques**, exports | — |
| **Éditeur** (`editor`) | Créer, modifier, supprimer sur les clés, les attributions, les équipes et les membres ; **exporter les données** | Administrer les comptes, voir l'historique des actions, voir la synthèse globale et les statistiques — **ces menus lui sont masqués, pas grisés** |
| **Visiteur** (`visitor`) | **Lire** et **exporter les données** | Rien ajouter, rien modifier, rien supprimer, rien administrer — **menus masqués** |

Rôle par défaut à l'inscription : `visitor`.

Les **membres** dont on suit les clés (`User`, rattachés à une `Team`) ne sont pas des comptes :
ce sont des personnes gérées dans l'application, pas des utilisateurs de l'application.

## Product Purpose

Tenir à jour qui détient quelle clé physique des locaux de l'église, où se trouve chaque exemplaire
non attribué (armoire ou coffre), et garder la trace de chaque mouvement.

Le succès : à tout moment, un responsable sait sans chercher combien d'exemplaires d'une clé existent,
lesquels sont sortis, à qui, depuis quand — et peut le prouver via l'historique.

**Le portail remplace un fichier Excel.** C'est l'étalon à battre : tout flux plus lent ou plus lourd
que la ligne équivalente dans un tableur est un échec fonctionnel, quelle que soit sa qualité visuelle.

## Positioning

Registre de clés adossé à la structure réelle de l'église : les clés sont modélisées en trois niveaux
(**type de clé** → **exemplaire physique** → **attribution**), et les détenteurs sont organisés en
équipes de service. Un tableur ou un outil d'inventaire générique ne restitue ni la distinction
type/exemplaire, ni la traçabilité nominative par équipe, ni le journal d'actions horodaté.

## Operating Context

- **En production, réellement utilisé**, avec des données réelles et de l'historique accumulé.
- Les clés physiques sont stockées à deux emplacements nommés : **Armoire** et **Coffre**.
  Un exemplaire attribué passe en localisation **Utilisateur** ; sa localisation d'origine est
  mémorisée pour être restaurée au retour.
- La saisie se fait après coup, au bureau, plutôt qu'au moment de la remise de main à main.
- Amorçage et reprise de données par import de fichiers Excel (`import_key`, `import_team`,
  `import_team_members`), pas par saisie initiale à la main.
- Déploiement Docker (conteneur `django-keyapp-python-1`) via `deploy.sh`, sur NAS/serveur interne
  (`/volume1/keyapp/`), mise à jour par `git pull` + redémarrage du conteneur.

### Matériel réel

**Portable modeste, petit écran (~1366 px), machine modérée.** Contrainte de conception directe :
les tableaux ne doivent pas déborder horizontalement à cette largeur, et les pages doivent rester
légères. Ne jamais concevoir pour un 1920 px confortable.

### Volumes mesurés (`merchex/db.sqlite3`, relevé le 2026-08-28)

| Table | Lignes |
|---|---|
| Types de clés | **148** |
| Exemplaires | **890** |
| Attributions | **494** |
| Membres | **67** |
| Équipes | **25** |
| Comptes gestionnaires | **5** |
| Actions journalisées | **829** |

Ces volumes sont **nettement supérieurs à l'estimation de mémoire** (~50 types / ~150 exemplaires).
Conséquence : recherche, filtrage, tri, pagination et densité ne sont pas du confort, ce sont des
fonctions critiques — sur un écran de 1366 px, 890 exemplaires ne se parcourent pas à l'œil.

## Capabilities and Constraints

Fonctionnalités confirmées (routes existantes) :

- Parc de clés : liste, création, modification, suppression unitaire et en masse ; quantités totales
  réparties entre armoire et coffre ; état de chaque exemplaire (Neuf / Bon / Moyen / Mauvais).
- Attribution : affectation d'exemplaires à un membre, retrait total des clés d'un membre,
  consultation des clés d'un membre (vues et endpoints AJAX dédiés).
- Membres et équipes : CRUD, rattachement membre ↔ équipe, filtrage des membres par équipe.
- Gestionnaires (comptes) : création, modification, suppression — administrateurs uniquement.
- Authentification complète : connexion, inscription + validation, profil, réinitialisation de mot de
  passe par email (envoi via un compte Gmail applicatif « Django EERE App »), page d'accès refusé.
- Tableaux de bord distincts par rôle (`admin_dashboard`, `editor_dashboard`).
- Stock, tableau de synthèse et export des données.
- Historique des actions (`ActionLog`) : journal horodaté avec auteur, rôle, type d'action, objet,
  anciennes/nouvelles valeurs ; détail, statistiques, recherche API et export CSV. Admins uniquement.

Cycle de vie physique à porter dans l'outil :

- **Une clé perdue ou cassée reste dans l'inventaire avec son statut** — elle ne disparaît pas de la
  vue. L'écart entre exemplaires théoriques et exemplaires réellement disponibles doit rester lisible.
- **Refaire un double est un événement produit** : le total d'exemplaires du type évolue, et
  l'historique doit permettre d'expliquer pourquoi.

Contraintes techniques :

- Django + templates HTML, **CSS écrit à la main dans chaque page**, aucun build front
  (pas de bundler, pas de framework JS). FontAwesome 6 et Google Fonts en CDN.
- 19 pages étendent `merchex/listings/templates/listings/base.html`.
- Base SQLite (`merchex/db.sqlite3`).
- **Interface, libellés, messages et emails en français uniquement** — pas d'i18n multilingue prévue.

Règles de rôle appliquées (2026-08-28) :

- **Visiteur en lecture seule, appliqué côté serveur.** Le décorateur `write_required`
  (`listings/views.py`) refuse au visiteur toute vue qui écrit : création, modification et
  suppression de clés, membres et équipes, attribution et retrait de clés, ainsi que la page
  d'attribution elle-même. Réponse `403` JSON sur les appels AJAX, redirection vers
  `access_denied` sinon.
- **Menus masqués, jamais grisés** : « Gestion des clés attribuées » et la carte d'accueil
  correspondante disparaissent pour le visiteur. Les boutons Ajouter / Modifier / Retirer sont
  retirés des pages clés, équipes et détenteurs — y compris dans les lignes rendues en JavaScript.
- **« Gestion des détenteurs de clés » est consultable par les trois rôles**, sans les actions pour
  le visiteur. Le menu et la carte d'accueil étaient réservés à l'administrateur ; ils sont
  désormais ouverts, ce qui rend aussi la page visible à l'éditeur — cohérent avec le fait qu'il
  gère les membres.
- **Le visiteur garde son profil et les exports.**
- Couvert par `listings/tests.py` (13 tests) : le masquage est un confort d'affichage, ce sont les
  tests serveur qui font foi.

Matrice des rôles, telle qu'appliquée :

| | Comptes | Historique + Statistiques | Synthèse globale | Écriture |
|---|---|---|---|---|
| **Administrateur** | ✓ | ✓ | ✓ | ✓ |
| **Éditeur** | ✗ | ✗ | ✓ | ✓ |
| **Visiteur** | ✗ | ✗ | ✓ lecture + export | ✗ |

L'éditeur fait tout sauf administrer les comptes et consulter le journal des actions ; la synthèse
globale est de la consultation, ouverte aux trois rôles.

Défauts corrigés le 2026-08-28 :

- `assign_keys` n'est plus `@csrf_exempt`. L'exemption ouvrait l'endpoint le plus sensible du
  portail aux requêtes forgées, alors que ses deux appelants réels envoyaient déjà le jeton.
- **L'historique ne perdait plus seulement des lignes : il perdait toutes les actions sur les
  comptes.** `get_model_fields_dict` employait `field.verbose_name` comme clé de dictionnaire ; sur
  `Owner`, qui hérite d'`AbstractUser`, dix de ces libellés sont des traductions paresseuses
  (`__proxy__`). `json.dumps` échouait, l'exception était avalée par un `except` muet, et la ligne
  `ActionLog` n'était jamais créée. Les clés sont désormais forcées en texte, et l'échec de
  journalisation est tracé avec sa pile complète.
- `utils.py` contenait une seconde définition de `log_action`, une seconde de
  `get_model_fields_dict` et une classe `HistoryMiddleware` morte (le middleware réellement branché
  est `listings.middleware.HistoryMiddleware`). Corriger la mauvaise copie n'aurait rien changé.

Écarts restants (à traiter comme dette, pas comme spécification) :

- Le contrôle de rôle dans `LoginRequiredMiddleware` porte sur le préfixe `/owners/`, qui
  n'existe dans aucune route : c'est du code mort.
- `users copy.html` est un gabarit orphelin qui contient encore un formulaire vers `assign_keys`.
- `merchex/db.sqlite3` est suivi par git alors que `.gitignore` déclare `*.sqlite3` : le fichier a
  été committé avant la règle. Un `git add -A` embarque donc la base de production.

**Rien n'est décidé** au-delà de la consolidation de l'existant : pas de notifications ou rappels
email, pas de QR codes ou étiquettes, pas d'ouverture de comptes aux membres détenteurs. Ne rien
présenter comme prévu. Restent également non tranchés : la centralisation des tokens CSS et un
usage mobile élargi.

## Brand Commitments

- Nom affiché : **EERE** (logo texte dans l'en-tête) — Église Évangélique Rencontre Espérance,
  mention en pied de page.
- **L'identité visuelle actuelle fait autorité et doit être préservée.**
  [DESIGN.md](DESIGN.md) / [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) sont la source de vérité :
  vert teal `#3a9f87` (primaire), survol `#2a7562`, gradient signature
  `linear-gradient(135deg, #0d3028 0%, #1a5040 100%)`, orange accent `#FFA500`,
  rouge danger `#dc2626`.
- Polices de marque : **DM Serif Display** (titres) + **DM Sans** (interface).
- **Ton chaleureux et communautaire** : accueillant et humain, propre à une église, tout en restant
  clair et professionnel. Vouvoiement, vocabulaire métier assumé (gestionnaire, équipe, clé, armoire,
  coffre). Ni administratif froid, ni familier.
- **Le mot de la maison est « registre », jamais « parc ».** « Parc » vient de la gestion
  d'actifs — parc automobile, parc informatique : du matériel garé qu'on inventorie une fois
  l'an. Ici les clés sont dans les mains de personnes et changent de main à chaque
  arrivée, départ ou changement d'équipe. « Registre » porte le mouvement et les porteurs ;
  « parc » les efface. Vocabulaire retenu : registre, clé, modèle, exemplaire, détenteur,
  équipe, armoire, coffre.

## Evidence on Hand

- `DESIGN_SYSTEM.md` (copié en `DESIGN.md`) — relevé complet de la palette, des composants et de
  l'état actuel : cohérent mais non centralisé (`#3a9f87` répété ~38×, `#0d3028` ~49× en dur).
- Données réelles en base (`merchex/db.sqlite3`, volumes ci-dessus) et jeux d'import Excel dans
  `merchex/listings/data/`.
- Capture HTML du site public de l'église : `www.egliseevangeliqueparis12.org-20260308T015006.html`.
- Aucun témoignage, chiffre d'usage, benchmark ou engagement de niveau de service n'existe :
  ne rien inventer de tel dans une interface ou une page.

## Product Principles

1. **Plus rapide que le tableur, sinon rien.** Les gestionnaires viennent d'Excel et peuvent y
   retourner ; chaque flux se juge au nombre de gestes par rapport à une ligne de tableur.
2. **La vérité du registre prime sur la mise en avant.** L'écran répond « où est cette clé, qui l'a »
   avant toute autre ambition ; c'est un outil de travail, pas une vitrine.
3. **Type, exemplaire, attribution restent distincts.** Aucune vue ne doit aplatir ces trois niveaux :
   c'est ce qui rend l'inventaire exact — et ce qu'aucun tableur ne sait faire.
4. **La saisie doit pouvoir s'achever.** Un mouvement commencé et abandonné en cours est la panne
   principale : parcours courts, état sauvegardable, jamais de tunnel qui punit l'interruption.
5. **Toute action laisse une trace lisible.** L'historique est une fonctionnalité produit, pas un log
   technique : consultable et compréhensible par un non-technicien.
6. **Le rôle se voit par ce qui est absent.** Ce qu'un rôle ne peut pas faire est masqué, jamais
   grisé ni découvert par un refus.
7. **Rien qui exige un build.** Toute évolution tient en Django + HTML + CSS écrit à la main, sur un
   portable modeste.
8. **Personne ne doit être indispensable.** L'interface doit s'expliquer seule : si un seul référent
   sait s'en servir, l'outil a échoué.

## Accessibility & Inclusion

Aucune norme formelle n'a été retenue. Exigences réelles issues du terrain : public adulte non
technique et peu à l'aise, écran ~1366 px, interface intégralement en français. Priorité aux
libellés en clair, aux cibles de clic généreuses et aux messages d'erreur qui disent quoi faire.

### Sensibilité des données

**Savoir qui détient les clés du bâtiment est une information de sécurité des locaux.** Jamais
d'exposition publique, jamais de vue accessible sans authentification, prudence sur ce qui part en
export ou en capture. Aucune contrainte réglementaire formelle n'a été posée par ailleurs : la
séparation des trois rôles est le mécanisme de protection retenu.

## Failure Modes

Signaux d'échec nommés par le porteur du produit, à surveiller dans toute décision de conception :

- **Retour à Excel** — l'outil est contourné parce qu'il est plus lent.
- **Dérive entre la base et le réel** — la base dit une chose, l'armoire une autre ; la confiance
  dans l'affichage s'effondre.
- **Un seul référent** — l'outil devient dépendant d'une personne ; en son absence tout s'arrête.
- **Saisie abandonnée en cours** — les mouvements sont faits mais pas enregistrés, parce que c'est
  trop long au moment où ça arrive.
