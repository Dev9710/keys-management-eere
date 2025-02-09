from .models import Key
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, CharField, F
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Key, User, Team
from .forms import KeyForm, UserForm
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone


def hello(request):
    # bands = Band.objects.all()
    return render(request, 'listings/hello.html')


def about(request):
    return HttpResponse('<h1>A propos de</h1> <p> Nous aimons  merchex </p>')


def home(request):
    return render(request, 'listings/home.html')


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
    keys = Key.objects.all().order_by('number')  # Toutes les clés existantes
    form = KeyForm()  # Formulaire vide pour ajouter une nouvelle clé
    keys_count = keys.count()

    # Récupérer les numéros déjà utilisés
    used_numbers = Key.objects.values_list('number', flat=True)

    # Trouver les 10 premiers numéros disponibles
    # Exemple : numéros possibles de 1 à 999
    all_possible_numbers = range(1, 1000)
    available_numbers = [
        num for num in all_possible_numbers if num not in used_numbers][:10]

    # Filtrer les clés non attribuées
    available_keys = Key.objects.filter(is_assigned=False).order_by('number')

    context = {
        'keys': keys,
        'keys_count': keys_count,
        'form': form,
        'available_keys': available_keys,
        # Passer les numéros disponibles au template
        'available_numbers': available_numbers,

    }
    return render(request, 'listings/keys.html', context)


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
    return render(request, 'listings/attribute.html', {'users': users})


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
    users = []  # Initialiser une liste vide pour les utilisateurs

    # Récupérer toutes les équipes pour les filtres
    teams = Team.objects.all()

    # Filtrer par équipe si une équipe est sélectionnée
    if team_id:
        team = get_object_or_404(Team, id=team_id)
        # Filtrer les utilisateurs par équipe
        users = User.objects.filter(team=team)
    else:
        # Si aucune équipe n'est sélectionnée, ne pas montrer d'utilisateurs
        users = []

    # Filtrer les clés attribuées par utilisateur si un utilisateur est sélectionné
    if user_id:
        user = get_object_or_404(User, id=user_id)
        assigned_keys = Key.objects.filter(assigned_user=user)

        # Filtrer les clés non attribuées et exclure celles déjà attribuées à cet utilisateur
        keys = Key.objects.filter(is_assigned=False).exclude(
            id__in=[key.id for key in assigned_keys])

    context = {
        'teams': teams,
        'users': users,
        'keys': keys,
        'assigned_keys': assigned_keys,
        'user_id': user_id,
        'team_id': team_id,
        'user': user,
    }

    return render(request, 'listings/attribute.html', context)


def get_users_by_team(request, team_id):
    try:
        # Récupérer les membres de l'équipe avec les champs requis
        team_members = User.objects.filter(team_id=team_id).values(
            'id', 'firstname', 'name')

        # Formatter les données pour l'API
        users_list = [{
            'id': member['id'],
            'name': f"{member['firstname']} {member['name']}"
        } for member in team_members]

        return JsonResponse({'users': users_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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
                     key.number} a été supprimée avec succès")

    # Rediriger vers la liste des clés ou une page appropriée.
    return redirect('key_list')


# used
def get_assigned_keys(request, user_id):
    if not user_id:
        return JsonResponse({"error": "User ID is required"}, status=400)

    try:
        keys = Key.objects.filter(assigned_user_id=user_id)
        keys_data = [{
            "id": key.id,
            "number": key.number,
            "name": key.name,
            "key_used": key.key_used,
            "place": key.place,
            "assigned_date": key.assigned_date.strftime('%d-%m-%Y') if key.assigned_date else None,
            'comments': key.comments
        } for key in keys]

        return JsonResponse({"assigned_keys": keys_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


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


# used
def get_modal_assigned_keys(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Obtenir la date courante
    current_date = timezone.now().date().isoformat()

    # Récupérer les clés assignées à l'utilisateur
    assigned_keys = Key.objects.filter(assigned_user=user)
    assigned_keys_ids = list(assigned_keys.values_list('id', flat=True))

    # Récupérer les clés non assignées
    available_keys = Key.objects.filter(assigned_user=None)

    return JsonResponse({
        'assigned_keys': [
            {
                'id': key.id,
                'number': key.number,
                'name': key.name,
                'place': key.place,
                'assigned_date': key.assigned_date.isoformat() if key.assigned_date else "Aucune date",
                'comments': key.comments,
            } for key in assigned_keys
        ],
        'available_keys': [
            {'id': key.id, 'number': key.number, 'name': key.name, 'place': key.place} for key in available_keys
        ],
        'assigned_keys_ids': assigned_keys_ids,
        'current_date': current_date
    })

# used


def assign_keys(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        selected_keys = data.get('selected_keys', [])
        assignment_date = data.get('assignment_date', timezone.now().date())

        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'Utilisateur non spécifié'
            }, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Utilisateur non trouvé'
            }, status=404)

        # Récupérer toutes les clés actuellement attribuées à l'utilisateur
        current_keys = Key.objects.filter(assigned_user=user)

        # Désattribuer les clés qui ne sont plus sélectionnées
        current_keys.exclude(id__in=selected_keys).update(
            assigned_user=None,
            assigned_date=None
        )

        # Attribuer les nouvelles clés sélectionnées
        Key.objects.filter(id__in=selected_keys).update(
            assigned_user=user,
            assigned_date=assignment_date
        )

        # Récupérer la liste mise à jour des clés
        updated_keys = []
        for key in Key.objects.filter(assigned_user=user):
            updated_keys.append({
                'id': key.id,
                'number': key.number,
                'name': key.name,
                'place': key.place,
                'formatted_date': key.assigned_date.strftime('%d/%m/%Y') if key.assigned_date else None,
                'comments': key.comments,
            })

        return JsonResponse({
            'success': True,
            'message': 'Clés mises à jour avec succès',
            'updated_keys': updated_keys
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=500)


def user_list(request):
    # Récupérer tous les utilisateurs avec leurs équipes
    users = User.objects.select_related('team').all()
    teams = Team.objects.all()
    users_count = users.count()

    # Récupérer les paramètres GET
    user_id = request.GET.get('user_id', None)
    team_id = request.GET.get('team_id', None)

    # Filtrer les utilisateurs si une équipe est sélectionnée
    if team_id:
        team = get_object_or_404(Team, id=team_id)
        users = users.filter(team=team)

    # Récupérer un utilisateur spécifique si `user_id` est passé
    selected_user = None
    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
    # Passer les données au template
    context = {
        'users_count': users_count,
        'teams': teams,
        'users': users,
        'user_id': user_id,
        'team_id': team_id,
        'selected_user': selected_user,
        'selected_team_id': team_id,
    }

    return render(request, 'listings/users.html', context)


@require_POST
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Supprimer le user
    user.delete()

    # Ajouter un message de confirmation
    messages.success(request, f"L'utiisateur {
                     user.firstname} a été supprimée avec succès.")

    # Rediriger vers la liste de user
    return redirect('user_list')


def user_team(request):
    team_id = request.GET.get('team_id', None)

    if team_id:
        team = get_object_or_404(Team, id=team_id)
        users = User.objects.filter(team=team)
    else:
        users = User.objects.all()

    # Créer une liste d'utilisateurs sous forme de dictionnaire
    user_list = [
        {
            'id': user.id,
            'name': user.name,
            'firstname': user.firstname,
            'team': user.team.name if user.team else 'Aucune équipe',
            'team_id': user.team.id if user.team else None,  # Ajout de l'ID de l'équipe
            'comment': user.comment,
        }
        for user in users
    ]

    # Retourner une réponse JSON
    return JsonResponse({'users': user_list})


def user_update(request):
    if request.method == 'POST':
        print("Données POST reçues:", request.POST)  # Debug log
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'Utilisateur non spécifié.'
            }, status=400)

        user = get_object_or_404(User, id=user_id)
        form = UserForm(request.POST, instance=user)

        print("Form data:", form.data)  # Debug log
        print("Form is valid:", form.is_valid())  # Debug log

        if not form.is_valid():
            print("Form errors:", form.errors)  # Debug log

        if form.is_valid():
            user = form.save()
            print("User après sauvegarde:", user.team)  # Debug log
            return JsonResponse({
                'success': True,
                'message': 'Utilisateur mis à jour avec succès.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la modification.',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)


def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)  # Get the data from the form
        if form.is_valid():  # Validate the form
            form.save()  # Save the new key
            messages.success(request, 'Utilisateur ajoutée avec succès.')
            return redirect('user_list')  # Redirect to the key list page
        else:
            print(form.errors)
            messages.error(
                request, "Erreur lors de l\'ajout de l'utilisateur.")
    return redirect('user_list')  # If not POST, redirect back to the key list
