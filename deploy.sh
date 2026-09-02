#!/bin/bash
#
# Déploiement du portail EERE sur le NAS.
#
# La production tourne sur MySQL : l'application démarre sous
# merchex.settings_nas et parle au conteneur merchex-db. Les données vivent
# dans le volume Docker merchex_mysql_data, hors d'atteinte de git.
#
# Le script raconte ce qu'il fait, étape par étape, et s'arrête à la
# première qui échoue en expliquant dans quel état il laisse le système.
# C'est ce qui permet de savoir, en cas de pépin, si le site tourne encore
# et sur quelle version.
#
# À lancer avec sudo : docker exige root sur DSM.

set -uo pipefail

DEPOT=/volume1/keyapp/keys-management-eere
CONTENEUR=django-keyapp-python-1
CONTENEUR_DB=merchex-db
SAUVEGARDES=/volume1/keyapp/sauvegardes   # hors du dépôt, exprès :
                                          # une sauvegarde dedans serait
                                          # emportée par un pull.
A_GARDER=10
TOTAL_ETAPES=7

# Identifiants MySQL : surchargeables par l'environnement, valeurs du
# docker-compose par défaut.
MYSQL_BASE="${MYSQL_DATABASE:-merchex}"
MYSQL_UTILISATEUR="${MYSQL_USER:-merchex}"
MYSQL_MOTDEPASSE="${MYSQL_PASSWORD:-password}"

# ── Affichage ────────────────────────────────────────────────────────
# Couleurs seulement si l'on écrit vers un terminal : redirigé dans un
# fichier ou un courriel, le journal reste lisible.
if [ -t 1 ]; then
    GRAS=$'\e[1m'; VERT=$'\e[32m'; ROUGE=$'\e[31m'; JAUNE=$'\e[33m'
    GRIS=$'\e[90m'; FIN=$'\e[0m'
else
    GRAS=""; VERT=""; ROUGE=""; JAUNE=""; GRIS=""; FIN=""
fi

BARRE="══════════════════════════════════════════════════════════════"

ETAPE_COURANTE=0
NOM_ETAPE=""
APP_ARRETEE=0        # l'application a-t-elle été arrêtée par ce script ?
CODE_MODIFIE=0       # le git pull est-il passé ?
CIBLE=""             # chemin de la sauvegarde, une fois prise
AVANT=""
APRES=""
LIGNES=""

etape() {
    ETAPE_COURANTE=$((ETAPE_COURANTE + 1))
    NOM_ETAPE="$1"
    printf "\n%s─── Étape %d sur %d ─── %s%s\n" \
        "$GRAS" "$ETAPE_COURANTE" "$TOTAL_ETAPES" "$NOM_ETAPE" "$FIN"
    # Une phrase qui dit pourquoi cette étape existe, pas seulement ce
    # qu'elle fait : c'est ce qui manque quand on relit un journal a froid.
    printf "%s    %s%s\n\n" "$GRIS" "$2" "$FIN"
}

ok()     { printf "    %s✔%s  %s\n" "$VERT" "$FIN" "$1"; }
info()   { printf "    %s·%s  %s\n" "$GRIS" "$FIN" "$1"; }
alerte() { printf "    %s!%s  %s\n" "$JAUNE" "$FIN" "$1"; }

# Sortie en échec : dit où ça a cassé, ce qui s'est passé, dans quel état
# est le site, et quoi faire. C'est le seul chemin de sortie en erreur.
echec() {
    cause="$1"
    conseil="${2:-}"

    printf "\n%s%s%s%s\n" "$GRAS" "$ROUGE" "$BARRE" "$FIN"
    printf "%s%s  LE DÉPLOIEMENT S'EST ARRÊTÉ%s\n" "$GRAS" "$ROUGE" "$FIN"
    printf "%s%s%s%s\n" "$GRAS" "$ROUGE" "$BARRE" "$FIN"

    printf "\n  %sOù%s\n" "$GRAS" "$FIN"
    printf "    À l'étape %d sur %d : %s\n" "$ETAPE_COURANTE" "$TOTAL_ETAPES" "$NOM_ETAPE"

    printf "\n  %sCe qui s'est passé%s\n" "$GRAS" "$FIN"
    printf "    %s\n" "$cause"

    printf "\n  %sDans quel état est le site%s\n" "$GRAS" "$FIN"
    if [ "$APP_ARRETEE" -eq 0 ]; then
        printf "    Le site fonctionne normalement, comme avant le lancement de\n"
        printf "    ce script. Ni le code, ni la base, ni les conteneurs n'ont\n"
        printf "    été touchés. Vous pouvez relancer sans risque.\n"
    elif [ "$CODE_MODIFIE" -eq 0 ]; then
        printf "    Le site est HORS LIGNE : je l'avais arrêté pour remplacer le\n"
        printf "    code, mais le code n'a pas été modifié.\n"
        printf "\n    Pour le remettre en ligne tout de suite, sur la version\n"
        printf "    actuelle et sans rien changer :\n"
        printf "        %sdocker start %s%s\n" "$GRAS" "$CONTENEUR" "$FIN"
    else
        printf "    Le site est HORS LIGNE, et le code a déjà été mis à jour\n"
        printf "    (version %s).\n" "$(git rev-parse --short HEAD 2>/dev/null)"
        printf "\n    Pour le remettre en ligne sur la nouvelle version :\n"
        printf "        %sdocker start %s%s\n" "$GRAS" "$CONTENEUR" "$FIN"
        printf "\n    Pour revenir à la version précédente :\n"
        printf "        %sgit reset --hard %s && docker start %s%s\n" \
            "$GRAS" "${AVANT:-HEAD~1}" "$CONTENEUR" "$FIN"
    fi

    if [ -n "$CIBLE" ] && [ -s "$CIBLE" ]; then
        printf "\n  %sVotre sauvegarde%s\n" "$GRAS" "$FIN"
        printf "    La base a bien été sauvegardée avant l'incident, ici :\n"
        printf "        %s\n" "$CIBLE"
        printf "    Pour la restaurer si un jour c'était nécessaire :\n"
        printf "        gzip -dc %s \\\\\n" "$CIBLE"
        printf "          | docker exec -i %s mysql -u%s -p %s\n" \
            "$CONTENEUR_DB" "$MYSQL_UTILISATEUR" "$MYSQL_BASE"
    fi

    if [ -n "$conseil" ]; then
        printf "\n  %sCe que vous pouvez faire%s\n" "$GRAS" "$FIN"
        printf "    %s\n" "$conseil"
    fi
    printf "\n"
    exit 1
}

DEBUT=$(date +%s)

printf "%s%s%s\n" "$GRAS" "$BARRE" "$FIN"
printf "%s  Déploiement du portail EERE%s\n" "$GRAS" "$FIN"
printf "%s%s%s\n" "$GRAS" "$BARRE" "$FIN"
printf "%s  Ce script récupère la nouvelle version du code et la met en\n" "$GRIS"
printf "  ligne. Il sauvegarde d'abord la base de données, puis coupe le\n"
printf "  site le temps de remplacer le code, et le remet en ligne.\n"
printf "  Comptez environ une minute d'indisponibilité.%s\n\n" "$FIN"
printf "  Dépôt         %s\n" "$DEPOT"
printf "  Application   %s\n" "$CONTENEUR"
printf "  Base          %s (MySQL, base « %s »)\n" "$CONTENEUR_DB" "$MYSQL_BASE"
printf "  Lancé le      %s\n" "$(date '+%d/%m/%Y à %H:%M:%S')"

cd "$DEPOT" || { echo "Dépôt introuvable : $DEPOT"; exit 1; }

# ── 1 ────────────────────────────────────────────────────────────────
etape "Je vérifie que tout est en place" \
      "Avant de toucher à quoi que ce soit, je m'assure que Docker répond et que les deux conteneurs sont bien là."

if ! docker info >/dev/null 2>&1; then
    echec "Docker ne me répond pas." \
          "Relancez le script avec sudo — sur DSM, Docker n'est accessible qu'en root : sudo ./deploy.sh"
fi
ok "Docker me répond."

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEUR_DB" 2>/dev/null)" != "true" ]; then
    echec "Le conteneur de la base de données ($CONTENEUR_DB) ne tourne pas. Je ne peux donc pas la sauvegarder, et je refuse de déployer sans sauvegarde." \
          "Démarrez la base puis relancez : docker start $CONTENEUR_DB"
fi
ok "La base de données ($CONTENEUR_DB) est allumée."

if ! docker inspect "$CONTENEUR" >/dev/null 2>&1; then
    echec "Je ne trouve aucun conteneur nommé $CONTENEUR." \
          "Vérifiez son nom exact avec : docker ps -a"
fi
ok "L'application ($CONTENEUR) existe."

AVANT=$(git rev-parse --short HEAD)
info "Le site tourne actuellement sur la version $AVANT — « $(git log -1 --pretty=%s) »"

# ── 2 ────────────────────────────────────────────────────────────────
etape "Je sauvegarde la base de données" \
      "C'est votre filet de sécurité. Rien ne sera modifié tant que cette sauvegarde n'est pas faite ET vérifiée."

mkdir -p "$SAUVEGARDES"
CIBLE="$SAUVEGARDES/merchex-$(date +%Y%m%d-%H%M%S).sql.gz"
info "Copie de la base « $MYSQL_BASE » en cours, patientez..."

# --single-transaction lit toutes les tables dans une même vue cohérente
# sans poser de verrou : l'application peut continuer d'écrire pendant le
# dump. MYSQL_PWD plutôt que -p en argument, qui exposerait le mot de passe
# dans la liste des processus du NAS.
#
# --no-tablespaces : depuis MySQL 5.7, mysqldump interroge les espaces de
# tables, ce qui exige le privilège global PROCESS. L'utilisateur merchex
# n'a de droits que sur sa base, et doit le rester.
docker exec -e MYSQL_PWD="$MYSQL_MOTDEPASSE" "$CONTENEUR_DB" \
    mysqldump --single-transaction --no-tablespaces \
              --user="$MYSQL_UTILISATEUR" "$MYSQL_BASE" \
    2>/tmp/deploy-dump.err | gzip > "$CIBLE"
RES_DUMP=${PIPESTATUS[0]}

if [ "$RES_DUMP" -ne 0 ] || [ ! -s "$CIBLE" ]; then
    DETAIL=$(head -3 /tmp/deploy-dump.err 2>/dev/null)
    rm -f "$CIBLE"; CIBLE=""
    echec "La sauvegarde a échoué : mysqldump s'est arrêté en erreur (code $RES_DUMP).${DETAIL:+
    Message de MySQL : $DETAIL}" \
          "Le déploiement s'arrête ici, volontairement : pas de sauvegarde, pas de déploiement."
fi

# Un dump peut sortir sans erreur et ne rien contenir d'utile — mauvaise
# base, droits insuffisants. On vérifie qu'il porte bien la table des
# exemplaires avant de lui faire confiance.
NB_TABLES=$(gzip -dc "$CIBLE" | grep -c '^CREATE TABLE')
if ! gzip -dc "$CIBLE" | grep -q 'CREATE TABLE .listings_keyinstance.'; then
    echec "La sauvegarde s'est bien écrite, mais elle ne contient pas la table des exemplaires de clés. Elle ne vaut donc rien, et je ne vais pas déployer en m'appuyant dessus." \
          "Le fichier est conservé pour analyse : $CIBLE"
fi

ok "Sauvegarde terminée : $(du -h "$CIBLE" | cut -f1), $NB_TABLES tables."
ok "Elle est ici : $CIBLE"

# On ne conserve que les dernières.
ls -1t "$SAUVEGARDES"/merchex-*.sql.gz 2>/dev/null \
    | tail -n +$((A_GARDER + 1)) \
    | while read -r vieille; do rm -f -- "$vieille"; done
NB_SAUV=$(ls -1 "$SAUVEGARDES"/merchex-*.sql.gz 2>/dev/null | wc -l)
info "Je conserve les $A_GARDER sauvegardes les plus récentes (il y en a $NB_SAUV)."

# ── 3 ────────────────────────────────────────────────────────────────
etape "Je coupe le site" \
      "Le temps de remplacer le code. Sans cette coupure, l'application servirait un code à moitié remplacé."

if docker stop "$CONTENEUR" >/dev/null 2>&1; then
    APP_ARRETEE=1
    ok "Application arrêtée. À partir d'ici, le site est hors ligne."
else
    APP_ARRETEE=1
    alerte "L'application était déjà arrêtée. Je continue."
fi

# ── 4 ────────────────────────────────────────────────────────────────
etape "Je récupère la nouvelle version du code" \
      "C'est le git pull. La base de données n'est pas concernée : elle vit dans un volume Docker, git n'y a pas accès."

SORTIE_PULL=$(git pull 2>&1)
if [ $? -ne 0 ]; then
    printf "%s\n" "$SORTIE_PULL" | sed "s/^/    /"
    echec "git pull a échoué : le code n'a pas pu être mis à jour." \
          "Réglez le conflit ci-dessus, puis relancez le script. En attendant, vous pouvez remettre le site en ligne sur l'ancienne version."
fi
CODE_MODIFIE=1
APRES=$(git rev-parse --short HEAD)

if [ "$AVANT" = "$APRES" ]; then
    alerte "Aucun nouveau commit : le code était déjà à jour ($APRES)."
    info "Le site sera quand même redémarré, donc les migrations seront rejouées."
else
    NB_COMMITS=$(git rev-list --count "$AVANT..$APRES")
    ok "$NB_COMMITS nouveau(x) commit(s) récupéré(s). Version $AVANT → $APRES."
    printf "\n"
    git log --oneline "$AVANT..$APRES" | sed "s/^/        $GRIS/;s/\$/$FIN/"
    printf "\n"

    # Une migration non appliquée fait planter les pages concernées. Elle
    # sera jouée au redémarrage par l'entrypoint, mais autant le savoir.
    NB_MIGRATIONS=$(git diff --name-only --diff-filter=A "$AVANT..$APRES" \
        -- 'merchex/listings/migrations/*.py' | wc -l)
    if [ "$NB_MIGRATIONS" -gt 0 ]; then
        alerte "Cette mise à jour contient $NB_MIGRATIONS nouvelle(s) migration(s) : la structure de la base va changer au redémarrage."
    else
        info "Aucune migration : la structure de la base ne change pas."
    fi
fi

# ── 5 ────────────────────────────────────────────────────────────────
etape "Je vérifie que la base répond toujours" \
      "Un dernier contrôle avant de laisser la nouvelle version écrire dedans."

LIGNES=$(docker exec -e MYSQL_PWD="$MYSQL_MOTDEPASSE" "$CONTENEUR_DB" \
    mysql --batch --skip-column-names --user="$MYSQL_UTILISATEUR" "$MYSQL_BASE" \
          -e "select count(*) from listings_keyinstance;" 2>/dev/null)

if [ -z "$LIGNES" ] || [ "$LIGNES" -eq 0 ] 2>/dev/null; then
    echec "La base est vide ou ne répond plus. Je laisse l'application arrêtée plutôt que de la laisser écrire dans une base dans cet état." \
          "N'redémarrez pas l'application tant que ce n'est pas élucidé. Votre sauvegarde de tout à l'heure est intacte."
fi
ok "La base répond : $LIGNES exemplaires de clés enregistrés."

# ── 6 ────────────────────────────────────────────────────────────────
etape "Je remets le site en ligne" \
      "Au démarrage, le conteneur applique d'abord les migrations, puis lance le serveur uWSGI."

if ! docker start "$CONTENEUR" >/dev/null 2>&1; then
    echec "Le démarrage de l'application a échoué." \
          "Regardez le journal du conteneur : docker logs --tail 50 $CONTENEUR"
fi
APP_ARRETEE=0
ok "Commande de démarrage envoyée."

# ── 7 ────────────────────────────────────────────────────────────────
etape "Je m'assure que le site est bien reparti" \
      "Un conteneur qui plante au démarrage le fait dans les premières secondes. J'attends de voir uWSGI démarrer avant de conclure."

info "J'observe le démarrage pendant quelques secondes..."
for _ in $(seq 1 20); do
    sleep 1
    ETAT=$(docker inspect -f '{{.State.Running}}' "$CONTENEUR" 2>/dev/null)
    [ "$ETAT" != "true" ] && break
    docker logs --tail 40 "$CONTENEUR" 2>&1 | grep -q "Start uWSGI" && break
done

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEUR" 2>/dev/null)" != "true" ]; then
    printf "\n%s\n" "$(docker logs --tail 25 "$CONTENEUR" 2>&1 | sed 's/^/    /')"
    echec "L'application s'est arrêtée juste après son démarrage. Le journal ci-dessus montre pourquoi." \
          "Pour revenir à la version qui fonctionnait : git reset --hard $AVANT && docker start $CONTENEUR"
fi
ok "Le conteneur tourne."

if docker logs --tail 60 "$CONTENEUR" 2>&1 | grep -q "Start uWSGI"; then
    ok "Le serveur uWSGI a démarré : le site répond."
else
    alerte "uWSGI n'a pas encore signalé son démarrage. Ce n'est pas forcément grave, mais surveillez : docker logs -f $CONTENEUR"
fi

TRACES=$(docker logs --tail 60 "$CONTENEUR" 2>&1 \
    | grep -E "Applying |No migrations to apply|DB is up" | tail -5)
if [ -n "$TRACES" ]; then
    printf "\n    Ce que le démarrage a fait :\n"
    printf "%s\n" "$TRACES" | sed "s/^/        $GRIS/;s/\$/$FIN/"
fi

# ── Résumé ───────────────────────────────────────────────────────────
DUREE=$(( $(date +%s) - DEBUT ))
printf "\n%s%s%s%s\n" "$GRAS" "$VERT" "$BARRE" "$FIN"
printf "%s%s  DÉPLOIEMENT TERMINÉ — le site est en ligne%s\n" "$GRAS" "$VERT" "$FIN"
printf "%s%s%s%s\n" "$GRAS" "$VERT" "$BARRE" "$FIN"
printf "  Version       %s → %s\n" "$AVANT" "$APRES"
printf "  Dernier ajout « %s »\n" "$(git log -1 --pretty=%s)"
printf "  Sauvegarde    %s\n" "$CIBLE"
printf "  Base          %s exemplaires de clés\n" "$LIGNES"
printf "  Durée         %s secondes\n" "$DUREE"
printf "\n  %sPensez à ouvrir le site pour vérifier de vos yeux.%s\n\n" "$GRIS" "$FIN"
