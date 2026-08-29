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

. $Activation

# manage.py pose déjà ce réglage par défaut, mais pas les scripts lancés
# directement par python : on l'aligne pour que tout parte du même endroit.
$env:DJANGO_SETTINGS_MODULE = 'merchex.settings_local'

$VersionPython = (python --version) 2>&1
$VersionDjango = (python -c "import django; print(django.get_version())" 2>$null)

Write-Host ""
Write-Host "  Portail EERE - environnement actif" -ForegroundColor Green
Write-Host "     $VersionPython  |  Django $VersionDjango"
Write-Host "     reglages : $env:DJANGO_SETTINGS_MODULE"
Write-Host ""
Write-Host "  Commandes courantes, depuis le dossier merchex :"
Write-Host "     cd merchex"
Write-Host "     python manage.py runserver"
Write-Host "     python manage.py test listings.tests"
Write-Host "     python manage.py makemigrations ; python manage.py migrate"
Write-Host ""
Write-Host "  Pour sortir : deactivate"
Write-Host ""
