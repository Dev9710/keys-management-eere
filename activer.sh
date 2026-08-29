# Active l'environnement Python du portail EERE (Git Bash / WSL).
#
#   source ./activer.sh        ou, en plus court :   . ./activer.sh
#
# Pourquoi « source » : activer un venv modifie les variables du shell
# courant. Lancé normalement (./activer.sh), le script tourne dans un
# processus fils et son activation disparaît avec lui.

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo ""
    echo "  Ce script doit être sourcé, pas exécuté."
    echo "  Tapez plutôt :  source ./activer.sh"
    echo ""
    exit 1
fi

# Le venv est cherché à côté de ce fichier : le script marche depuis
# n'importe quel répertoire courant.
_racine="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_venv="$_racine/.venv-eere"

# Windows met les binaires dans Scripts/, Linux et macOS dans bin/.
if   [ -f "$_venv/Scripts/activate" ]; then _activation="$_venv/Scripts/activate"
elif [ -f "$_venv/bin/activate" ];     then _activation="$_venv/bin/activate"
else
    echo ""
    echo "  Environnement introuvable : $_venv"
    echo "  Pour le créer :"
    echo "     python -m venv .venv-eere"
    echo "     source ./activer.sh"
    echo "     pip install -r merchex/requirements.txt"
    echo ""
    unset _racine _venv
    return 1
fi

# Un autre environnement déjà actif fausse tout : on le signale.
if [ -n "${VIRTUAL_ENV:-}" ] && [ "$VIRTUAL_ENV" != "$_venv" ]; then
    echo ""
    echo "  Attention : un autre environnement est actif"
    echo "     $VIRTUAL_ENV"
    echo "  Il est remplacé. En cas de doute : deactivate, puis on recommence."
fi

# shellcheck disable=SC1090
. "$_activation"

# bash retient le chemin des commandes déjà appelées. Sans ce vidage, un
# « python » lancé avant l'activation continue de pointer sur l'interpréteur
# système, alors que le prompt affiche (.venv-eere).
hash -r 2>/dev/null || true

# manage.py pose déjà ce réglage par défaut, mais pas les scripts lancés
# directement par python : on l'aligne pour que tout parte du même endroit.
export DJANGO_SETTINGS_MODULE=merchex.settings_local

_py="$(python --version 2>&1)"
_dj="$(python -c 'import django; print(django.get_version())' 2>/dev/null)"

# Le script vérifie son propre travail : « python » doit désormais être
# celui du venv. Si ce n'est pas le cas — hachage bash récalcitrant, PATH
# détourné, autre venv — on le dit au lieu de laisser croire que tout va
# bien parce que le prompt affiche (.venv-eere).
_reel="$(python -c 'import sys; print(sys.executable)' 2>/dev/null)"
case "$_reel" in
    *".venv-eere"*) _ok=1 ;;
    *)              _ok=0 ;;
esac

echo ""
echo "  Portail EERE — environnement actif"
echo "     $_py  |  Django ${_dj:-absent}"
echo "     réglages : $DJANGO_SETTINGS_MODULE"
echo ""
echo "  Commandes, depuis n'importe quel dossier :"
echo "     manage runserver"
echo "     manage test listings.tests"
echo "     manage makemigrations && manage migrate"
echo ""
echo "  Pour sortir : deactivate"
echo ""

if [ "$_ok" -ne 1 ]; then
    echo "  ATTENTION : « python » ne pointe pas sur cet environnement"
    echo "     python  -> ${_reel:-introuvable}"
    echo "     attendu -> $_venv"
    echo ""
    echo "  Utilisez « manage », qui appelle le bon interpréteur par son"
    echo "  chemin absolu et ne peut pas être détourné. Pour « pip »,"
    echo "  passez par :  \$EERE_PYTHON -m pip install ..."
    echo ""
fi

# « manage » appelle l'interpréteur du venv et manage.py par leur chemin
# absolu : ni le répertoire courant ni l'ordre du PATH ne peuvent le
# détourner. manage.py vit dans merchex/, pas à la racine.
EERE_PYTHON="${_venv}/Scripts/python.exe"
[ -x "$EERE_PYTHON" ] || EERE_PYTHON="${_venv}/bin/python"
EERE_MANAGE="$_racine/merchex/manage.py"
export EERE_PYTHON EERE_MANAGE

manage() {
    if [ ! -f "$EERE_MANAGE" ]; then
        echo "manage.py introuvable : $EERE_MANAGE" >&2
        return 1
    fi
    ( cd "$(dirname "$EERE_MANAGE")" && "$EERE_PYTHON" manage.py "$@" )
}

unset _racine _venv _activation _py _dj _reel _ok
