from django.contrib import messages
from django.shortcuts import redirect

# ================================
# 3. MIDDLEWARE POUR CAPTURER L'UTILISATEUR COURANT
# ================================


class LoginRequiredMiddleware:
    """
    Middleware qui assure que toutes les pages non publiques nécessitent une connexion.
    Vérifie également les permissions basées sur le rôle pour certaines URLs.
    """

    def __init__(self, get_response):
        """
        Initialisation du middleware avec la liste des URLs publiques.
        Le paramètre get_response est la fonction qui sera appelée après ce middleware.
        """
        self.get_response = get_response
        # Liste des URLs qui ne nécessitent pas d'authentification
        self.public_urls = [
            '/login/',
            '/register/',
            '/logout/',
            '/admin/login/',
            '/static/',
            '/media/',  # Pour les fichiers média
            '/favicon.ico',  # Pour l'icône du site

            # Ajouter les URLs de réinitialisation de mot de passe
            '/password-reset/',
            '/password-reset/done/',
            '/password-reset-confirm/',
            '/password-reset-complete/',
        ]

    def __call__(self, request):
        """
        Méthode appelée pour chaque requête HTTP.
        Vérifie l'authentification et les permissions avant de traiter la requête.
        """
        # Récupération du chemin de la requête
        path = request.path_info

        # Permettre l'accès aux URLs publiques sans authentification
        if any(path.startswith(url) for url in self.public_urls):
            return self.get_response(request)

        # Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
        if not request.user.is_authenticated:
            messages.info(
                request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect('login')

        # Vérifier les autorisations basées sur le rôle
        if path.startswith('/owners/') and request.user.role != 'admin':
            messages.error(
                request, "Vous n'avez pas les droits nécessaires pour accéder à cette page.")
            return redirect('home')

        # Traiter la requête normalement si toutes les vérifications sont passées
        return self.get_response(request)


class HistoryMiddleware:
    """
    Middleware pour capturer l'utilisateur courant et l'associer aux actions
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Stocker l'utilisateur courant dans le thread local
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        response = self.get_response(request)

        # Nettoyer le thread local après la requête
        set_current_user(None)

        return response
