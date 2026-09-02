#!/bin/bash
#
# Déploiement du portail EERE sur le NAS.
#
# La production tourne sur MySQL depuis la migration : l'application
# démarre sous merchex.settings_nas et parle au conteneur merchex-db. Les
# données vivent dans le volume Docker merchex_mysql_data, hors d'atteinte
# de git — un pull ne peut donc pas les toucher.
#
# Ce script prend malgré tout un dump complet avant chaque déploiement, et
# refuse d'aller plus loin s'il n'a pas pu l'obtenir. Une base de clés
# perdue ne se reconstitue pas.

set -uo pipefail

DEPOT=/volume1/keyapp/keys-management-eere
CONTENEUR=django-keyapp-python-1
CONTENEUR_DB=merchex-db
SAUVEGARDES=/volume1/keyapp/sauvegardes   # hors du dépôt, exprès :
                                          # une sauvegarde dedans serait
                                          # emportée par un pull.
A_GARDER=10

# Identifiants MySQL : surchargeables par l'environnement, valeurs du
# docker-compose par défaut. À sortir du script le jour où le mot de passe
# sera changé — voir le .env évoqué dans le README.
MYSQL_BASE="${MYSQL_DATABASE:-merchex}"
MYSQL_UTILISATEUR="${MYSQL_USER:-merchex}"
MYSQL_MOTDEPASSE="${MYSQL_PASSWORD:-password}"

cd "$DEPOT" || exit 1

# ── 1. La base doit être debout avant tout ───────────────────────────
# Sans elle, pas de sauvegarde ; et sans sauvegarde, pas de déploiement.
if [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEUR_DB" 2>/dev/null)" != "true" ]; then
    echo "ERREUR : le conteneur $CONTENEUR_DB ne tourne pas."
    echo "Impossible de sauvegarder la base. Déploiement annulé."
    exit 1
fi

# ── 2. Sauvegarde, avant toute opération git ─────────────────────────
mkdir -p "$SAUVEGARDES"
HORODATAGE=$(date +%Y%m%d-%H%M%S)
CIBLE="$SAUVEGARDES/merchex-$HORODATAGE.sql.gz"

# --single-transaction lit toutes les tables dans une même vue cohérente
# sans poser de verrou : l'application peut continuer d'écrire pendant le
# dump. MYSQL_PWD plutôt que -p en argument, qui exposerait le mot de
# passe dans la liste des processus du NAS.
#
# --no-tablespaces : depuis MySQL 5.7, mysqldump interroge les espaces de
# tables, ce qui exige le privilège global PROCESS. L'utilisateur merchex
# n'a de droits que sur sa propre base — et c'est très bien ainsi. Sans
# cette option le dump echoue sur « Access denied ... PROCESS ». Ces
# métadonnées ne concernent que les tables InnoDB à espace dédié, que
# Django ne crée pas.
#
# Pas de --routines : dumper les procédures stockées réclame là aussi des
# droits supplémentaires, et l'application n'en a aucune.
docker exec -e MYSQL_PWD="$MYSQL_MOTDEPASSE" "$CONTENEUR_DB" \
    mysqldump --single-transaction --no-tablespaces \
              --user="$MYSQL_UTILISATEUR" "$MYSQL_BASE" \
    | gzip > "$CIBLE"

if [ "${PIPESTATUS[0]}" -ne 0 ] || [ ! -s "$CIBLE" ]; then
    echo "ERREUR : la sauvegarde MySQL a échoué. Déploiement annulé."
    rm -f "$CIBLE"
    exit 1
fi

# Un dump peut sortir sans erreur et pourtant ne rien contenir d'utile —
# mauvaise base, droits insuffisants. On vérifie qu'il porte bien la table
# des exemplaires avant de lui faire confiance.
if ! gzip -dc "$CIBLE" | grep -q 'CREATE TABLE .listings_keyinstance.'; then
    echo "ERREUR : le dump ne contient pas listings_keyinstance."
    echo "Sauvegarde suspecte, déploiement annulé : $CIBLE"
    exit 1
fi

TAILLE=$(du -h "$CIBLE" | cut -f1)
echo "Base sauvegardée : $CIBLE ($TAILLE)"

# On ne conserve que les dernières.
ls -1t "$SAUVEGARDES"/merchex-*.sql.gz 2>/dev/null \
    | tail -n +$((A_GARDER + 1)) \
    | while read -r vieille; do rm -f -- "$vieille"; done

# ── 3. Arrêt du conteneur applicatif ─────────────────────────────────
# Le temps du pull, pour ne pas servir un code à moitié remplacé.
docker stop "$CONTENEUR" >/dev/null 2>&1 && echo "Conteneur arrêté."

# ── 4. Mise à jour du code ───────────────────────────────────────────
if ! git pull; then
    echo "ERREUR : git pull a échoué. Le code n'a pas été mis à jour."
    echo "La base est intacte, sauvegarde disponible : $CIBLE"
    docker start "$CONTENEUR" >/dev/null 2>&1
    echo "Conteneur redémarré sur l'ancienne version."
    exit 1
fi

# ── 5. Contrôle de la base avant de laisser Django y toucher ─────────
LIGNES=$(docker exec -e MYSQL_PWD="$MYSQL_MOTDEPASSE" "$CONTENEUR_DB" \
    mysql --batch --skip-column-names --user="$MYSQL_UTILISATEUR" "$MYSQL_BASE" \
          -e "select count(*) from listings_keyinstance;" 2>/dev/null)

if [ -z "$LIGNES" ] || [ "$LIGNES" -eq 0 ] 2>/dev/null; then
    echo "ERREUR : la base est vide ou injoignable. Conteneur laissé arrêté."
    echo "Restauration possible depuis $CIBLE :"
    echo "  gzip -dc $CIBLE | docker exec -i $CONTENEUR_DB \\"
    echo "      mysql -u$MYSQL_UTILISATEUR -p $MYSQL_BASE"
    exit 1
fi
echo "Base vérifiée : $LIGNES exemplaires."

# ── 6. Redémarrage ───────────────────────────────────────────────────
docker start "$CONTENEUR"
