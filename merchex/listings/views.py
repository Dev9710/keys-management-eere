from .models import Key
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Key, User, Team
from .forms import KeyForm
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt


def hello(request):
    bands = Band.objects.all()
    return render(request, 'listings/hello.html', {'bands': bands})


def about(request):
    return HttpResponse('<h1>A propos de</h1> <p> Nous aimons  merchex </p>')


def listing(request):
    listings = Listing.objects.all()
    return HttpResponse(f"""'<h1>Listing!</h1>
                        <p>Mes listings :<p>
                <ul>
                    <li>{listings[0].title}</li>
                    <li>{listings[1].title}</li>
                    <li>{listings[2].title}</li>
                </ul>
                """)


def contact(request):
    return HttpResponse('<h1> contact us </h1> <p> </>')


def key_list(request):
    keys = Key.objects.all().order_by('number')  # Get all keys from the database
    form = KeyForm()  # Create an empty form for adding a new key

    # Filtrer les clés non attribuées pour l’attribution
    available_keys = Key.objects.filter(is_assigned=False).order_by('number')

    return render(request, 'listings/keys.html', {'keys': keys, 'form': form, 'available_keys': available_keys})


def key_delete(request, key_id):
    # Get the key object or raise a 404 if not found
    key = get_object_or_404(Key, id=key_id)

    try:
        # Attempt to delete the key
        key.delete()

        # Add a success message if deletion is successful
        messages.success(request, f'La clé numéro {
                         key.number} a été supprimée avec succès !')

    except Exception as e:
        # Add an error message if the deletion fails
        messages.error(request, f'Échec de la suppression de la clé numéro {
                       key.number}. Erreur: {str(e)}')

    # Redirect to the key list view (or another view)
    # Replace 'key_list' with your actual view name
    return redirect('key_list')


def key_create(request):
    if request.method == 'POST':
        form = KeyForm(request.POST)  # Get the data from the form
        if form.is_valid():  # Validate the form
            form.save()  # Save the new key
            messages.success(request, 'Clé ajoutée avec succès.')
            return redirect('key_list')  # Redirect to the key list page
        else:
            print(form.errors)
            messages.error(request, 'Erreur lors de l\'ajout de la clé.')
    return redirect('key_list')  # If not POST, redirect back to the key list


def key_update(request):
    if request.method == 'POST':
        key_id = request.POST.get('key_id')
        if not key_id:
            messages.error(request, 'Clé non spécifiée.')
            return redirect('key_list')
        key = get_object_or_404(Key, id=key_id)
        form = KeyForm(request.POST, instance=key)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clé mise à jour avec succès.')
        else:
            # Log des erreurs pour le débogage
            print(form.errors)
            messages.error(
                request, 'Erreur lors de la modification de la clé.')
    return redirect('key_list')


def users(request):
    if request.method == "POST":
        form = User(request.POST)
        if form.is_valid():
            form.save()
            # Handle success (e.g., redirect or display a message)
    else:
        form = User()
    return render(request, 'listings/users.html', {'users': users})


def teams(request):
    teams = Team.objects.all()
    return render(request, 'listings/teams.html', {'teams': teams})


def user_keys_view(request):
    # Récupérer les paramètres depuis la requête
    user_id = request.GET.get('user_id', None)
    team_id = request.GET.get('team_id', None)

    # Initialiser les variables
    assigned_keys = []
    keys = []
    user = None

    # Filtrer par équipe si une équipe est sélectionnée
    if team_id:
        team = get_object_or_404(Team, id=team_id)

        # Filtrer les utilisateurs par équipe
        users = User.objects.filter(team=team)

        # Filtrer les clés non attribuées par équipe
        keys = Key.objects.filter(
            assigned_user__team=team, is_assigned=False).distinct()

    else:
        # Récupérer tous les utilisateurs si aucune équipe n'est sélectionnée
        users = User.objects.all()
        keys = Key.objects.filter(is_assigned=False).distinct()

    # Filtrer les clés attribuées par utilisateur si un utilisateur est sélectionné
    if user_id:
        user = get_object_or_404(User, id=user_id)
        assigned_keys = Key.objects.filter(assigned_user=user).distinct()

        if team_id:
            assigned_keys = Key.objects.filter(
                assigned_user=user, assigned_user__team=team).distinct()
        else:
            assigned_keys = Key.objects.filter(userkey__user=user).distinct()

         # Filtrer les clés non attribuées et exclure celles déjà attribuées à cet utilisateur
        keys = Key.objects.filter(is_assigned=False).exclude(
            id__in=[key.id for key in assigned_keys])

    # Récupérer toutes les équipes pour les filtres
    teams = Team.objects.all()

    # Passer les données au template
    context = {
        'teams': teams,
        'users': users,
        'keys': keys,  # Clés non attribuées
        'assigned_keys': assigned_keys,  # Clés attribuées à l'utilisateur
        'user_id': user_id,
        'team_id': team_id,
        'user': user,  # Ajout explicite de l'utilisateur
    }

    return render(request, 'listings/users.html', context)


def get_users_by_team(request, team_id):
    # Récupérer les membres de l'équipe avec les champs requis
    team_members = User.objects.filter(team_id=team_id).values(
        'id', 'firstname', 'name', 'comment')

    # Utiliser une clé unique avec le prénom et nom
    unique_members = {}
    for member in team_members:
        # Clé basée sur firstname et name
        key = (member['firstname'], member['name'])
        if key not in unique_members:
            unique_members[key] = member

    # Convertir en liste de membres uniques
    members_list = list(unique_members.values())
    print("Membres uniques envoyés :", members_list)

    return JsonResponse({'users': members_list})


def get_keys_by_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    keys = user.keys.all().values('id', 'number', 'name', 'key_used', 'place')
    keys_list = list(keys)
    return JsonResponse({'keys': keys_list})


@require_POST
def key_delete(request, key_id):
    key = get_object_or_404(Key, id=key_id)

    # Supprimer la clé, qu'elle soit attribuée ou non
    key.delete()

    # Ajouter un message de confirmation
    messages.success(request, f"La clé numéro {
                     key.number} a été supprimée avec succès.")

    # Rediriger vers la liste des clés ou une page appropriée.
    return redirect('key_list')


def get_assigned_keys(request, user_id):
    if request.method == 'GET':
        keys = Key.objects.filter(assigned_user_id=user_id)
        keys_data = [
            {
                "id": key.id,
                "number": key.number,
                "name": key.name,
                "key_used": key.key_used,
                "place": key.place
            }
            for key in keys
        ]
        return JsonResponse({"assigned_keys": keys_data})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def modal_user_keys(request):
    teams = Team.objects.all()
    users = User.objects.all()
    selected_team_id = request.GET.get('team_id')
    selected_user_id = request.GET.get('user_id')

    assigned_keys = []
    keys = Key.objects.all()

    if selected_user_id:
        user = User.objects.get(id=selected_user_id)
        assigned_keys = Key.objects.filter(assigned_user=user)

    return render(request, 'listings/users.html', {
        'teams': teams,
        'users': users,
        'assigned_keys': assigned_keys,
        'keys': keys,
        'selected_team_id': selected_team_id,
        'selected_user_id': selected_user_id,
    })


def bulk_key_delete(request):
    if request.method == "POST":
        try:
            # Récupérer les clés depuis le champ caché
            keys_to_delete = json.loads(
                request.POST.get('keys_to_delete', '[]'))

            if not keys_to_delete:
                return JsonResponse({'error': 'Aucune clé sélectionnée.'}, status=400)

            # Supprimer les clés dans la base de données
            Key.objects.filter(id__in=keys_to_delete).delete()

            return JsonResponse({'message': 'Clés supprimées avec succès.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Requête non valide.'}, status=400)


def assign_keys_to_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        selected_keys = request.POST.getlist('selected_keys')

        if not user_id or not selected_keys:
            messages.error(
                request, "Veuillez sélectionner un utilisateur et des clés.")
            return redirect('user_keys')

        user = get_object_or_404(User, id=user_id)

        for key_id in selected_keys:
            if key_id:
                key = get_object_or_404(Key, id=key_id)
                key.assigned_user = user  # Assigner la clé à l'utilisateur
                key.is_assigned = True
                key.save()

        messages.success(request, "Les clés ont été attribuées avec succès.")
        return redirect('user_keys')


def get_modal_assigned_keys(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Récupérer les clés assignées à l'utilisateur
    assigned_keys = Key.objects.filter(assigned_user=user)
    assigned_keys_ids = list(assigned_keys.values_list(
        'id', flat=True))  # Convertir en liste pour JSON

    # Récupérer les clés non assignées
    available_keys = Key.objects.filter(assigned_user=None)
    print("Assigned keys:", list(assigned_keys))
    # Vérifiez que cette liste n'est pas vide
    print("Available keys:", list(available_keys))
    return JsonResponse({
        'assigned_keys': [
            {'id': key.id, 'number': key.number, 'name': key.name, 'place': key.place} for key in assigned_keys
        ],
        'available_keys': [
            {'id': key.id, 'number': key.number, 'name': key.name, 'place': key.place} for key in available_keys
        ],
        'assigned_keys_ids': assigned_keys_ids,
    })


def assign_keys(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    try:
        # Charger les données JSON du corps de la requête
        data = json.loads(request.body)

        # Extraire les informations nécessaires
        user_id = data.get('user_id')
        selected_keys = data.get('selected_keys')

        # Vérifier que les données sont présentes
        if not user_id or not selected_keys:
            return JsonResponse({'success': False, 'message': 'Utilisateur ou clés non spécifiés.'}, status=400)

        # Vérifier que l'utilisateur existe
        user = get_object_or_404(User, id=user_id)

        # Vérifier que les clés existent
        keys_to_assign = Key.objects.filter(id__in=selected_keys)
        if not keys_to_assign.exists():
            return JsonResponse({'success': False, 'message': 'Une ou plusieurs clés n\'existent pas.'}, status=404)

        # Assigner les clés à l'utilisateur
        keys_to_assign.update(assigned_user=user)

        # Récupérer les clés mises à jour pour l'affichage
        updated_keys = list(Key.objects.filter(
            assigned_user=user).values('id', 'number', 'name', 'place'))

        return JsonResponse({'success': True, 'updated_keys': updated_keys})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Erreur dans le format JSON.'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
