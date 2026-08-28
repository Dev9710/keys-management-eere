#!/bin/bash
#
# Déploiement du portail EERE sur le NAS.
#
# La base n'est plus suivie par git depuis le 28/08/2026 : un pull ne peut
# donc plus l'écraser. Ce script garde malgré tout une sauvegarde avant
# chaque déploiement, et remet la base en place si elle venait à disparaître.
# Une base de clés perdue ne se reconstitue pas.

set -uo pipefail

DEPOT=/volume1/keyapp/keys-management-eere
CONTENEUR=django-keyapp-python-1
BASE="$DEPOT/merchex/db.sqlite3"
SAUVEGARDES=/volume1/keyapp/sauvegardes   # hors du dépôt, exprès :
                                          # une sauvegarde dedans serait
                                          # emportée par un pull.
A_GARDER=10

cd "$DEPOT" || exit 1

# ── 1. Sauvegarde, avant toute opération git ─────────────────────────
if [ -f "$BASE" ]; then
    mkdir -p "$SAUVEGARDES"
    HORODATAGE=$(date +%Y%m%d-%H%M%S)
    CIBLE="$SAUVEGARDES/db-$HORODATAGE.sqlite3"

    # .backup lit la base de façon cohérente même si Django écrit pendant
    # ce temps ; un simple cp peut attraper un état intermédiaire.
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$BASE" ".backup '$CIBLE'"
    else
        cp -p "$BASE" "$CIBLE"
    fi

    if [ ! -s "$CIBLE" ]; then
        echo "ERREUR : la sauvegarde de la base a échoué. Déploiement annulé."
        exit 1
    fi
    echo "Base sauvegardée : $CIBLE"

    # On ne conserve que les dernières.
    ls -1t "$SAUVEGARDES"/db-*.sqlite3 2>/dev/null \
        | tail -n +$((A_GARDER + 1)) \
        | while read -r vieille; do rm -f -- "$vieille"; done
else
    echo "Avertissement : aucune base trouvée à $BASE"
fi

# ── 2. Arrêt du conteneur ────────────────────────────────────────────
# Django tient la base ouverte. Sous Linux, git peut supprimer un fichier
# ouvert : le conteneur continuerait alors d'écrire dans un fichier devenu
# fantôme, et au redémarrage Django, ne trouvant plus rien, créerait une
# base vide. Perte totale et silencieuse. On l'arrête donc avant le pull.
docker stop "$CONTENEUR" >/dev/null 2>&1 && echo "Conteneur arrêté."

# ── 3. Mise à jour du code ───────────────────────────────────────────
if ! git pull; then
    echo "ERREUR : git pull a échoué. Le code n'a pas été mis à jour."
    echo "La base est intacte, sauvegarde disponible dans $SAUVEGARDES."
    docker start "$CONTENEUR" >/dev/null 2>&1
    echo "Conteneur redémarré sur l'ancienne version."
    exit 1
fi

# ── 4. Filet : la base doit toujours être là après le pull ───────────
if [ ! -f "$BASE" ] && [ -d "$SAUVEGARDES" ]; then
    DERNIERE=$(ls -1t "$SAUVEGARDES"/db-*.sqlite3 2>/dev/null | head -1)
    if [ -n "$DERNIERE" ]; then
        cp -p "$DERNIERE" "$BASE"
        echo "La base avait disparu après le pull : restaurée depuis $DERNIERE"
    fi
fi

# ── 5. Contrôle avant de laisser Django y toucher ────────────────────
if command -v sqlite3 >/dev/null 2>&1 && [ -f "$BASE" ]; then
    LIGNES=$(sqlite3 "$BASE" "select count(*) from listings_keyinstance;" 2>/dev/null)
    if [ -z "$LIGNES" ] || [ "$LIGNES" -eq 0 ] 2>/dev/null; then
        echo "ERREUR : la base est vide ou illisible. Conteneur laissé arrêté."
        echo "Sauvegardes disponibles dans $SAUVEGARDES."
        exit 1
    fi
    echo "Base vérifiée : $LIGNES exemplaires."
fi

# ── 6. Redémarrage ───────────────────────────────────────────────────
docker start "$CONTENEUR"
