#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# backup_db.sh — Sauvegarde AUTOMATIQUE de la base, indépendante du déploiement.
#
# À planifier sur le NAS (Planificateur de tâches Synology), p. ex. 2×/mois.
# deploy.sh continue de sauvegarder à chaque déploiement ; ce script assure
# une sauvegarde régulière même quand l'appli est stable et qu'on ne déploie
# plus. Il n'arrête PAS l'application (dump à chaud, cohérent).
#
# Les sauvegardes automatiques vont dans un sous-dossier « auto/ » exprès :
# la rotation de deploy.sh purge « $SAUVEGARDES/merchex-*.sql.gz » à plat et
# ne descend pas dans auto/ — les deux jeux ne se marchent donc jamais dessus.
# ─────────────────────────────────────────────────────────────────────
set -uo pipefail

# ── Réglages (surchargeables par l'environnement) ────────────────────
CONTENEUR_DB="${CONTENEUR_DB:-merchex-db}"
SAUVEGARDES="${SAUVEGARDES:-/volume1/keyapp/sauvegardes}"
DEST="$SAUVEGARDES/auto"                 # sauvegardes automatiques, à part
A_GARDER="${A_GARDER_AUTO:-24}"          # ~1 an à 2 sauvegardes/mois
JOURNAL="$SAUVEGARDES/backup_db.log"

MYSQL_BASE="${MYSQL_DATABASE:-merchex}"
MYSQL_UTILISATEUR="${MYSQL_USER:-merchex}"
MYSQL_MOTDEPASSE="${MYSQL_PASSWORD:-password}"

# ── Journalisation ───────────────────────────────────────────────────
log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$JOURNAL"; }
mkdir -p "$DEST"

log "── Sauvegarde automatique de « $MYSQL_BASE » ──"

# ── Le conteneur de base tourne-t-il ? ───────────────────────────────
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTENEUR_DB"; then
    log "❌ ÉCHEC : le conteneur « $CONTENEUR_DB » ne tourne pas. Aucune sauvegarde prise."
    exit 1
fi

# ── Dump (mêmes options que deploy.sh, éprouvées) ────────────────────
# --single-transaction : vue cohérente sans verrou, l'appli peut écrire.
# --no-tablespaces : évite d'exiger le privilège global PROCESS.
# MYSQL_PWD : mot de passe hors de la liste des processus.
CIBLE="$DEST/merchex-$(date +%Y%m%d-%H%M%S).sql.gz"
ERRFILE="$(mktemp)"

docker exec -e MYSQL_PWD="$MYSQL_MOTDEPASSE" "$CONTENEUR_DB" \
    mysqldump --single-transaction --no-tablespaces \
              --user="$MYSQL_UTILISATEUR" "$MYSQL_BASE" \
    2>"$ERRFILE" | gzip > "$CIBLE"
RES=${PIPESTATUS[0]}

if [ "$RES" -ne 0 ] || [ ! -s "$CIBLE" ]; then
    DETAIL=$(head -3 "$ERRFILE" 2>/dev/null)
    rm -f "$CIBLE" "$ERRFILE"
    log "❌ ÉCHEC : mysqldump s'est arrêté (code $RES). ${DETAIL:+MySQL : $DETAIL}"
    exit 1
fi
rm -f "$ERRFILE"

# ── Vérification : le dump contient bien les données attendues ───────
# Un dump peut réussir et être vide (mauvaise base, droits). On exige la
# présence de la table des exemplaires de clés.
if ! gzip -dc "$CIBLE" | grep -q 'CREATE TABLE .listings_keyinstance.'; then
    log "❌ ÉCHEC : la sauvegarde ne contient pas la table des clés. Fichier conservé pour analyse : $CIBLE"
    exit 1
fi

TAILLE=$(du -h "$CIBLE" | cut -f1)
log "✅ Sauvegarde prise : $(basename "$CIBLE") ($TAILLE)"

# ── Rotation : ne garder que les A_GARDER plus récentes (dans auto/) ──
ls -1t "$DEST"/merchex-*.sql.gz 2>/dev/null \
    | tail -n +$((A_GARDER + 1)) \
    | while read -r vieux; do rm -f "$vieux" && log "🗑️  Purge : $(basename "$vieux")"; done

NB=$(ls -1 "$DEST"/merchex-*.sql.gz 2>/dev/null | wc -l)
log "Terminé. $NB sauvegarde(s) automatique(s) conservée(s) (plafond $A_GARDER)."
