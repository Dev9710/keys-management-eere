from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, CharField, F, Count
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import KeyType, KeyInstance, KeyAssignment, User, Team
from .forms import KeyForm, KeyInstanceForm, UserForm, TeamForm
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone


def hello(request):
    return render(request, 'listings/hello.html')


def about(request):
    return HttpResponse('<h1>A propos de</h1> <p> Nous aimons  merchex </p>')


def home(request):
    return render(request, 'listings/home.html')


def contact(request):
    return HttpResponse('<h1> contact us </h1> <p> </>')


def key_list(request):
    # Récupérer tous les types de clés
    key_types = KeyType.objects.all().order_by('number')
    form = KeyForm()
    keys_count = key_types.count()

    # Récupérer les numéros déjà utilisés
    used_numbers = KeyType.objects.values_list('number', flat=True)

    # Trouver les 10 premiers numéros disponibles
    all_possible_numbers = range(1, 1000)
    available_numbers = [
        num for num in all_possible_numbers if num not in used_numbers][:10]

    # Pour chaque type de clé, récupérer les informations sur les exemplaires
    key_types_with_data = []
    for key_type in key_types:
        # Calcul du nombre d'exemplaires attribués
        assigned_count = KeyInstance.objects.filter(
            key_type=key_type,
            is_available=False
        ).count()

        # Vérification de la cohérence des données
        is_consistent = (assigned_count + key_type.in_cabinet +
                         key_type.in_safe) == key_type.total_quantity

        consistency_message = ""
        if not is_consistent:
            calculated_total = assigned_count + key_type.in_cabinet + key_type.in_safe
            consistency_message = (
                f"Incohérence: total déclaré {key_type.total_quantity} != "
                f"somme des exemplaires (attribués: {assigned_count} + "
                f"armoire: {key_type.in_cabinet} + "
                f"coffre: {key_type.in_safe} = {calculated_total})"
            )

        key_types_with_data.append({
            'key_type': key_type,
            'assigned_count': assigned_count,
            'is_consistent': is_consistent,
            'consistency_message': consistency_message
        })

    context = {
        'keys': key_types_with_data,
        'keys_count': keys_count,
        'form': form,
        'available_numbers': available_numbers,
    }
    return render(request, 'listings/keys.html', context)


def key_create(request):
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            try:
                # Récupérer les données du formulaire
                key_type = form.save(commit=False)

                # Debug prints
                print(
                    f"Création - in_cabinet: {key_type.in_cabinet}, in_safe: {key_type.in_safe}")

                # S'assurer que les quantités sont cohérentes
                total_quantity = key_type.total_quantity
                in_cabinet = key_type.in_cabinet
                in_safe = key_type.in_safe

                # Vérifier si la somme cabinet + coffre est égale au total
                if (in_cabinet + in_safe) != total_quantity:
                    adjusted_total = in_cabinet + in_safe
                    messages.warning(request,
                                     f"Attention: la somme des exemplaires en armoire ({in_cabinet}) "
                                     f"et en coffre ({in_safe}) ne correspond pas au total ({total_quantity}). "
                                     f"Le total a été ajusté à {adjusted_total}.")
                    # Ajuster le total pour qu'il soit cohérent
                    key_type.total_quantity = adjusted_total

                # Enregistrer le type de clé
                key_type.save()

                # Créer les instances: d'abord celles dans l'armoire
                cabinet_instances = []
                for i in range(in_cabinet):
                    cabinet_instances.append(
                        KeyInstance(
                            key_type=key_type,
                            is_available=True,
                            condition='Bon',
                            location='Cabinet',
                            original_location='Cabinet'  # Ajouter l'emplacement d'origine
                        )
                    )

                # Puis celles dans le coffre
                safe_instances = []
                for i in range(in_safe):
                    safe_instances.append(
                        KeyInstance(
                            key_type=key_type,
                            is_available=True,
                            condition='Bon',
                            location='Coffre',
                            original_location='Coffre'  # Ajouter l'emplacement d'origine
                        )
                    )

                # Création en masse pour plus d'efficacité
                if cabinet_instances:
                    KeyInstance.objects.bulk_create(cabinet_instances)

                if safe_instances:
                    KeyInstance.objects.bulk_create(safe_instances)

                messages.success(request, 'Clé ajoutée avec succès.')
                return redirect('key_list')
            except Exception as e:
                print(f"Erreur lors de la création: {str(e)}")
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
        else:
            print(f"Erreurs de formulaire: {form.errors}")
            messages.error(request, 'Erreur lors de l\'ajout de la clé.')
    return redirect('key_list')


def key_update(request):
    if request.method == 'POST':
        key_id = request.POST.get('key_id')
        if not key_id:
            messages.error(request, 'Clé non spécifiée.')
            return redirect('key_list')

        key_type = get_object_or_404(KeyType, id=key_id)
        old_cabinet = key_type.in_cabinet
        old_safe = key_type.in_safe

        # Print for debugging
        print(
            f"Avant validation - in_cabinet: {key_type.in_cabinet}, in_safe: {key_type.in_safe}")
        print(f"POST data: {request.POST}")

        form = KeyForm(request.POST, instance=key_type)
        if form.is_valid():
            try:
                # Récupérer les données du formulaire avant de sauvegarder
                key_type = form.save(commit=False)

                # Print for debugging
                print(
                    f"Après validation - in_cabinet: {key_type.in_cabinet}, in_safe: {key_type.in_safe}")

                # Obtenir le nombre d'instances attribuées (qui ne doivent pas être supprimées)
                assigned_count = KeyInstance.objects.filter(
                    key_type=key_type, is_available=False).count()

                # S'assurer que les quantités sont cohérentes
                total_quantity = key_type.total_quantity
                in_cabinet = key_type.in_cabinet
                in_safe = key_type.in_safe
                storage_total = in_cabinet + in_safe

                # Vérifier si le nouveau total est suffisant pour couvrir les attributions existantes
                if storage_total + assigned_count != total_quantity:
                    # Ajuster le total pour qu'il soit cohérent
                    key_type.total_quantity = storage_total + assigned_count
                    messages.warning(request,
                                     f"Le total a été ajusté pour être cohérent avec la somme des exemplaires "
                                     f"(armoire: {in_cabinet}, coffre: {in_safe}, attribués: {assigned_count}).")

                # Enregistrer les modifications
                key_type.save()

                # Supprimer les instances non attribuées existantes
                # Important: Ne supprimez que les instances disponibles (is_available=True)
                KeyInstance.objects.filter(
                    key_type=key_type, is_available=True).delete()

                # Créer les nouvelles instances dans l'armoire
                cabinet_instances = []
                for i in range(in_cabinet):
                    cabinet_instances.append(
                        KeyInstance(
                            key_type=key_type,
                            is_available=True,
                            condition='Bon',
                            location='Cabinet'
                        )
                    )

                # Créer les nouvelles instances dans le coffre
                safe_instances = []
                for i in range(in_safe):
                    safe_instances.append(
                        KeyInstance(
                            key_type=key_type,
                            is_available=True,
                            condition='Bon',
                            location='Coffre'
                        )
                    )

                # Création en masse pour plus d'efficacité
                if cabinet_instances:
                    KeyInstance.objects.bulk_create(cabinet_instances)

                if safe_instances:
                    KeyInstance.objects.bulk_create(safe_instances)

                messages.success(request, 'Clé mise à jour avec succès.')
                return redirect('key_list')
            except Exception as e:
                print(f"Erreur lors de la mise à jour: {str(e)}")
                messages.error(
                    request, f'Erreur lors de la modification: {str(e)}')
        else:
            # Print errors for debugging
            print(f"Erreurs de formulaire: {form.errors}")
            messages.error(
                request, 'Erreur lors de la modification de la clé.')

    return redirect('key_list')


def users(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserForm()
    return render(request, 'listings/attribute.html', {'users': User.objects.all(), 'form': form})


def teams(request):
    teams = Team.objects.all()
    return render(request, 'listings/teams.html', {'teams': teams})


def user_keys_view(request):
    # Récupérer les paramètres depuis la requête
    user_id = request.GET.get('user_id', None)
    team_id = request.GET.get('team_id', None)

    # Initialiser les variables
    assigned_key_instances = []
    available_key_instances = []
    user = None
    users = []

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
        # Récupérer les instances de clés attribuées à cet utilisateur
        assignments = KeyAssignment.objects.filter(user=user, is_active=True)
        assigned_key_instances = [
            assignment.key_instance for assignment in assignments]

        # Récupérer les instances de clés disponibles (non attribuées)
        available_key_instances = KeyInstance.objects.filter(is_available=True)

    context = {
        'teams': teams,
        'users': users,
        'available_keys': available_key_instances,
        'assigned_keys': assigned_key_instances,
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
    # Récupérer les attributions actives
    assignments = KeyAssignment.objects.filter(user=user, is_active=True)
    keys_list = [{
        'id': assignment.key_instance.id,
        'number': assignment.key_instance.key_type.number,
        'name': assignment.key_instance.key_type.name,
        'place': assignment.key_instance.key_type.place,
        'location': assignment.key_instance.location
    } for assignment in assignments]

    return JsonResponse({'keys': keys_list})


@require_POST
def key_delete(request, key_id):
    key_type = get_object_or_404(KeyType, id=key_id)

    # Vérifier si des instances sont attribuées
    assigned_instances = KeyInstance.objects.filter(
        key_type=key_type,
        is_available=False
    ).exists()

    if assigned_instances:
        messages.error(request,
                       f"Impossible de supprimer la clé numéro {key_type.number}. Des exemplaires sont actuellement attribués.")
        return redirect('key_list')

    # Supprimer le type de clé et toutes ses instances
    key_type.delete()  # Cela supprimera également les instances en cascade

    messages.success(
        request, f"La clé numéro {key_type.number} a été supprimée avec succès.")
    return redirect('key_list')


def get_assigned_keys(request, user_id):
    if not user_id:
        return JsonResponse({"error": "User ID is required"}, status=400)

    try:
        user = get_object_or_404(User, id=user_id)
        # Récupérer les attributions actives
        assignments = KeyAssignment.objects.filter(user=user, is_active=True)
        keys_data = [{
            "id": assignment.key_instance.id,
            "number": assignment.key_instance.key_type.number,
            "name": assignment.key_instance.key_type.name,
            "place": assignment.key_instance.key_type.place,
            "location": assignment.key_instance.location,
            "assigned_date": assignment.assigned_date.strftime('%d-%m-%Y') if assignment.assigned_date else None,
            "comments": assignment.comments
        } for assignment in assignments]

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

            # Vérifier si des instances sont attribuées
            assigned_instances = KeyInstance.objects.filter(
                key_type_id__in=keys_to_delete,
                is_available=False
            ).exists()

            if assigned_instances:
                return JsonResponse(
                    {'error': 'Impossible de supprimer certaines clés. Des exemplaires sont actuellement attribués.'},
                    status=400
                )

            # Supprimer les types de clés
            KeyType.objects.filter(id__in=keys_to_delete).delete()

            return JsonResponse({'message': 'Clés supprimées avec succès.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Requête non valide.'}, status=400)


def get_modal_assigned_keys(request, user_id):
    user = get_object_or_404(User, id=user_id)
    current_date = timezone.now().date().isoformat()

    # Récupérer les instances de clés assignées à l'utilisateur
    assignments = KeyAssignment.objects.filter(user=user, is_active=True)
    assigned_key_instance_ids = [
        assignment.key_instance.id for assignment in assignments]

    # Récupérer les instances de clés disponibles (non assignées à aucun utilisateur)
    available_key_instances = KeyInstance.objects.filter(is_available=True)

    return JsonResponse({
        'assigned_keys': [
            {
                'id': assignment.key_instance.id,
                'number': assignment.key_instance.key_type.number,
                'name': assignment.key_instance.key_type.name,
                'place': assignment.key_instance.key_type.place,
                'location': assignment.key_instance.location,
                'assigned_date': assignment.assigned_date.isoformat() if assignment.assigned_date else "Aucune date",
                'comments': assignment.comments,
            } for assignment in assignments
        ],
        'available_keys': [
            {
                'id': instance.id,
                'number': instance.key_type.number,
                'name': instance.key_type.name,
                'place': instance.key_type.place,
                'location': instance.location
            } for instance in available_key_instances
        ],
        'assigned_keys_ids': assigned_key_instance_ids,
        'current_date': current_date
    })


def remove_all_keys(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        assignments = KeyAssignment.objects.filter(user=user, is_active=True)

        current_date = timezone.now().date()
        for assignment in assignments:
            assignment.is_active = False
            assignment.return_date = current_date
            assignment.save()  # Ceci déclenche la méthode save() de KeyInstance

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
def assign_keys(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        remove_all = data.get('remove_all', False)

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

        current_date = timezone.now().date()

        if remove_all:
            # Désactiver toutes les attributions actuelles
            assignments = KeyAssignment.objects.filter(
                user=user, is_active=True)
            for assignment in assignments:
                assignment.is_active = False
                assignment.return_date = current_date
                assignment.save()  # Cela va maintenant déclencher la mise à jour des compteurs
            return JsonResponse({
                'success': True,
                'message': 'Toutes les clés ont été retirées',
                'updated_keys': []
            })

        # Récupérer les instances de clés sélectionnées et la date d'attribution
        selected_key_instances = data.get('selected_keys', [])
        assignment_date = data.get('assignment_date', current_date)

        # Récupérer les attributions actuelles
        current_assignments = KeyAssignment.objects.filter(
            user=user, is_active=True)
        current_key_instance_ids = [
            assignment.key_instance_id for assignment in current_assignments]

        # Désactiver les attributions des clés qui ne sont plus sélectionnées
        keys_to_remove = [
            key_id for key_id in current_key_instance_ids if key_id not in selected_key_instances
        ]

        for assignment in KeyAssignment.objects.filter(
            user=user,
            key_instance_id__in=keys_to_remove,
            is_active=True
        ):
            assignment.is_active = False
            assignment.return_date = current_date
            assignment.save()  # La méthode save() va maintenant gérer les compteurs

        # Ajouter les nouvelles attributions
        for key_instance_id in selected_key_instances:
            if key_instance_id not in current_key_instance_ids:
                # Vérifier si l'instance est disponible
                try:
                    key_instance = KeyInstance.objects.get(
                        id=key_instance_id, is_available=True)

                    # Créer l'attribution - la méthode save() va maintenant gérer les compteurs
                    KeyAssignment.objects.create(
                        key_instance=key_instance,
                        user=user,
                        assigned_date=assignment_date,
                        is_active=True
                    )
                except KeyInstance.DoesNotExist:
                    # L'instance n'existe pas ou n'est pas disponible
                    continue

        # Récupérer la liste mise à jour des clés
        updated_assignments = KeyAssignment.objects.filter(
            user=user, is_active=True)
        updated_keys = []
        for assignment in updated_assignments:
            updated_keys.append({
                'id': assignment.key_instance.id,
                'number': assignment.key_instance.key_type.number,
                'name': assignment.key_instance.key_type.name,
                'place': assignment.key_instance.key_type.place,
                'location': assignment.key_instance.location,
                'formatted_date': assignment.assigned_date.strftime('%d/%m/%Y') if assignment.assigned_date else None,
                'comments': assignment.comments,
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

    # Vérifier si l'utilisateur a des clés assignées
    has_assigned_keys = KeyAssignment.objects.filter(
        user=user, is_active=True).exists()

    if has_assigned_keys:
        messages.error(
            request, f"Impossible de supprimer l'utilisateur {user.firstname}. Des clés lui sont actuellement attribuées.")
        return redirect('user_list')

    # Supprimer l'utilisateur
    user.delete()

    # Ajouter un message de confirmation
    messages.success(
        request, f"L'utilisateur {user.firstname} a été supprimé avec succès.")

    # Rediriger vers la liste des utilisateurs
    return redirect('user_list')


def user_team(request):
    team_id = request.GET.get('team_id', None)
    has_keys = request.GET.get('has_keys') == 'true'

    # Commencer avec tous les utilisateurs
    users = User.objects.all()

    # Filtrer par équipe si une équipe est sélectionnée
    if team_id:
        team = get_object_or_404(Team, id=team_id)
        users = users.filter(team=team)

    # Filtrer les utilisateurs qui ont des clés si le filtre est activé
    if has_keys:
        # Utilisateurs qui ont au moins une attribution de clé active
        users = users.filter(key_assignments__is_active=True).distinct()

    # Créer une liste d'utilisateurs sous forme de dictionnaire
    user_list = [
        {
            'id': user.id,
            'name': user.name,
            'firstname': user.firstname,
            'team': user.team.name if user.team else 'Aucune équipe',
            'team_id': user.team.id if user.team else None,
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
            messages.success(request, 'Utilisateur ajouté avec succès.')
            return redirect('user_list')  # Redirect to the key list page
        else:
            print(form.errors)
            messages.error(
                request, "Erreur lors de l\'ajout de l'utilisateur.")
    return redirect('user_list')  # If not POST, redirect back to the key list


def team_list(request):
    # Récupérer tous les utilisateurs avec leurs équipes
    users = User.objects.select_related('team').all()
    teams = Team.objects.all()
    teams_count = teams.count()

    # Récupérer les paramètres GET
    user_id = request.GET.get('user_id', None)
    team_id = request.GET.get('team_id', None)

    context = {
        'teams_count': teams_count,
        'teams': teams,
        'users': users,
        'user_id': user_id,
        'team_id': team_id,
        'selected_team_id': team_id,
    }

    return render(request, 'listings/teams.html', context)


@require_POST
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Vérifier si des utilisateurs sont dans cette équipe
    has_users = User.objects.filter(team=team).exists()

    if has_users:
        messages.error(
            request, f"Impossible de supprimer l'équipe {team.name}. Des utilisateurs y sont actuellement affectés.")
        return redirect('team_list')

    team.delete()
    messages.success(
        request, f"L'équipe {team.name} a été supprimée avec succès.")
    return redirect('team_list')


def team_update(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if not id:
            return JsonResponse({
                'success': False,
                'message': 'Équipe non spécifiée.'
            }, status=400)

        try:
            team = Team.objects.get(id=id)
            team.name = request.POST.get('name')
            team.save()

            return JsonResponse({
                'success': True,
                'message': 'Équipe mise à jour avec succès.'
            })
        except Team.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Équipe non trouvée.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)


def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)  # Get the data from the form
        if form.is_valid():  # Validate the form
            form.save()  # Save the new key
            messages.success(request, 'Équipe ajoutée avec succès.')
            return redirect('team_list')  # Redirect to the key list page
        else:
            print(form.errors)
            messages.error(
                request, "Erreur lors de l\'ajout de l'équipe.")
    return redirect('team_list')  # If not POST, redirect back to the key list
