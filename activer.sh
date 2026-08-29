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

# shellcheck disable=SC1090
. "$_activation"

# manage.py pose déjà ce réglage par défaut, mais pas les scripts lancés
# directement par python : on l'aligne pour que tout parte du même endroit.
export DJANGO_SETTINGS_MODULE=merchex.settings_local

_py="$(python --version 2>&1)"
_dj="$(python -c 'import django; print(django.get_version())' 2>/dev/null)"

echo ""
echo "  Portail EERE — environnement actif"
echo "     $_py  |  Django ${_dj:-absent}"
echo "     réglages : $DJANGO_SETTINGS_MODULE"
echo ""
echo "  Commandes courantes, depuis le dossier merchex :"
echo "     cd merchex"
echo "     python manage.py runserver"
echo "     python manage.py test listings.tests"
echo "     python manage.py makemigrations && python manage.py migrate"
echo ""
echo "  Pour sortir : deactivate"
echo ""

unset _racine _venv _activation _py _dj
