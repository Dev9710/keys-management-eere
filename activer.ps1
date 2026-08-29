# Active l'environnement Python du portail EERE.
#
#   . .\activer.ps1          <-- le point et l'espace sont obligatoires
#
# Pourquoi le point : activer un venv modifie les variables du shell courant.
# Lancé normalement (.\activer.ps1), le script tourne dans un processus fils
# et son activation disparaît avec lui. Le point le fait tourner ici même.

if ($MyInvocation.InvocationName -ne '.') {
    Write-Host ""
    Write-Host "  Ce script doit etre source, pas execute." -ForegroundColor Yellow
    Write-Host "  Tapez plutot :  . .\activer.ps1" -ForegroundColor Yellow
    Write-Host "                  ^ le point et l'espace comptent"
    Write-Host ""
    return
}

# Le venv est cherché à côté de ce fichier : le script marche depuis
# n'importe quel répertoire courant.
# Un autre environnement déjà actif fausse tout : on le signale.
$Racine = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Racine '.venv-eere'
$Activation = Join-Path $Venv 'Scripts\Activate.ps1'

if (-not (Test-Path $Activation)) {
    Write-Host ""
    Write-Host "  Environnement introuvable : $Venv" -ForegroundColor Red
    Write-Host "  Pour le creer :"
    Write-Host "     py -3.12 -m venv .venv-eere"
    Write-Host "     . .\activer.ps1"
    Write-Host "     pip install -r merchex\requirements.txt"
    Write-Host ""
    return
}

if ($env:VIRTUAL_ENV -and $env:VIRTUAL_ENV -ne $Venv) {
    Write-Host ""
    Write-Host "  Attention : un autre environnement est actif" -ForegroundColor Yellow
    Write-Host "     $env:VIRTUAL_ENV"
    Write-Host "  Il est remplace. En cas de doute : deactivate, puis on recommence."
}

. $Activation

# « manage » appelle l'interpréteur du venv et manage.py par leur chemin
# absolu : ni le répertoire courant ni l'ordre du PATH ne peuvent le
# détourner. manage.py vit dans merchex/, pas à la racine.
$global:EerePython = Join-Path $Venv 'Scripts\python.exe'
$global:EereManage = Join-Path $Racine 'merchex\manage.py'

function global:manage {
    if (-not (Test-Path $global:EereManage)) {
        Write-Host "manage.py introuvable : $($global:EereManage)" -ForegroundColor Red
        return
    }
    Push-Location (Split-Path -Parent $global:EereManage)
    try   { & $global:EerePython 'manage.py' @args }
    finally { Pop-Location }
}

# manage.py pose déjà ce réglage par défaut, mais pas les scripts lancés
# directement par python : on l'aligne pour que tout parte du même endroit.
$env:DJANGO_SETTINGS_MODULE = 'merchex.settings_local'

$VersionPython = (python --version) 2>&1
$VersionDjango = (python -c "import django; print(django.get_version())" 2>$null)

# Le script verifie son propre travail : « python » doit desormais etre
# celui du venv. Sinon on le dit, au lieu de laisser croire que tout va
# bien parce que le prompt affiche (.venv-eere).
$PythonReel = (python -c "import sys; print(sys.executable)" 2>$null)
$Aligne = $PythonReel -like "*.venv-eere*"

Write-Host ""
Write-Host "  Portail EERE - environnement actif" -ForegroundColor Green
Write-Host "     $VersionPython  |  Django $VersionDjango"
Write-Host "     reglages : $env:DJANGO_SETTINGS_MODULE"
Write-Host ""
Write-Host "  Commandes, depuis n'importe quel dossier :"
Write-Host "     manage runserver"
Write-Host "     manage test listings.tests"
Write-Host "     manage makemigrations ; manage migrate"
Write-Host ""
Write-Host "  Pour sortir : deactivate"
Write-Host ""

if (-not $Aligne) {
    Write-Host "  ATTENTION : « python » ne pointe pas sur cet environnement" -ForegroundColor Yellow
    Write-Host "     python  -> $PythonReel"
    Write-Host "     attendu -> $Venv"
    Write-Host ""
    Write-Host "  Utilisez « manage », qui appelle le bon interpreteur par son"
    Write-Host "  chemin absolu. Pour pip :  & `$EerePython -m pip install ..."
    Write-Host ""
}
