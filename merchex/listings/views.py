from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, CharField, F, Count
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import KeyType, KeyInstance, KeyAssignment, User, Team, Owner
from .forms import KeyForm, KeyInstanceForm, UserForm, TeamForm, CustomAuthenticationForm, CustomPasswordChangeForm
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .forms import OwnerCreationForm, OwnerUpdateForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from .utils import log_action, log_bulk_delete, log_password_change, log_password_reset
from .models import KeyType, KeyInstance, KeyAssignment, User, Team, Owner, ActionLog
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


class CustomPasswordResetView(PasswordResetView):
    """Vue pour demander la réinitialisation du mot de passe"""
    template_name = 'listings/password_reset_form.html'
    email_template_name = 'listings/password_reset_email.html'
    subject_template_name = 'listings/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Vue affichée après l'envoi du courriel de réinitialisation"""
    template_name = 'listings/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Vue pour le formulaire de saisie du nouveau mot de passe"""
    template_name = 'listings/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Vue confirmant que le mot de passe a été réinitialisé"""
    template_name = 'listings/password_reset_complete.html'


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

    # Dictionnaire pour associer chaque détenteur à son nombre de clés
    holders_count = {}

    # Liste complète de tous les détenteurs pour toutes les clés
    all_key_holders = []

    for key_type in key_types:
        # Calcul du nombre d'exemplaires attribués
        key_instances = KeyInstance.objects.filter(
            key_type=key_type,
            is_available=False
        )
        assigned_count = key_instances.count()

        # Récupérer les détenteurs de cette clé
        key_holders = []
        # Requête pour obtenir les utilisateurs qui détiennent des exemplaires de cette clé
        assignments = KeyAssignment.objects.filter(
            key_instance__key_type=key_type,
            is_active=True
        ).select_related('user')

        # Construire la liste des détenteurs
        for assignment in assignments:
            user = assignment.user
            holder_name = f"{user.firstname} {user.name}"
            key_holders.append({
                'id': user.id,
                'name': holder_name,
                'assignment_date': assignment.assigned_date.strftime('%d/%m/%Y') if assignment.assigned_date else "Date inconnue"
            })

            # Ajouter ou incrémenter le compteur pour ce détenteur
            if holder_name in holders_count:
                holders_count[holder_name] += 1
            else:
                holders_count[holder_name] = 1

            # Ajouter à la liste complète
            all_key_holders.append({
                'id': user.id,
                'name': holder_name,
                'key_number': key_type.number,
                'key_name': key_type.name,
                'assignment_date': assignment.assigned_date.strftime('%d/%m/%Y') if assignment.assigned_date else "Date inconnue"
            })

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
            'consistency_message': consistency_message,
            'key_holders': key_holders  # Ajouter la liste des détenteurs
        })

    # Convertir le dictionnaire des détenteurs en liste pour l'affichage
    holders_list = [{'name': name, 'count': count}
                    for name, count in holders_count.items()]
    # Trier par nombre de clés détenues (décroissant)
    holders_list.sort(key=lambda x: x['count'], reverse=True)

    context = {
        'keys': key_types_with_data,
        'keys_count': keys_count,
        'form': form,
        'available_numbers': available_numbers,
        'holders_count': holders_list,  # Ajouter les compteurs de détenteurs
        'all_key_holders': all_key_holders,  # Ajouter la liste complète des détenteurs
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

        # Récupérer l'objet KeyType existant
        key_type = get_object_or_404(KeyType, id=key_id)

        # Sauvegarder les valeurs originales avant la mise à jour
        old_total_quantity = key_type.total_quantity
        old_in_cabinet = key_type.in_cabinet
        old_in_safe = key_type.in_safe

        # Debug prints
        print(
            f"Avant validation - total: {old_total_quantity}, in_cabinet: {old_in_cabinet}, in_safe: {old_in_safe}")
        print(f"POST data: {request.POST}")

        # Appliquer les modifications du formulaire à l'objet
        form = KeyForm(request.POST, instance=key_type)

        if form.is_valid():
            try:
                # Récupérer les données du formulaire avant de sauvegarder
                key_type = form.save(commit=False)

                # Nouvelles valeurs après mise à jour du formulaire
                new_total_quantity = key_type.total_quantity
                new_in_cabinet = key_type.in_cabinet
                new_in_safe = key_type.in_safe

                # Vérifier si le nombre total d'exemplaires a augmenté
                if new_total_quantity > old_total_quantity:
                    # Calculer l'augmentation du nombre total d'exemplaires
                    quantity_increase = new_total_quantity - old_total_quantity

                    # Ajouter automatiquement cette augmentation au nombre de clés dans l'armoire
                    key_type.in_cabinet = old_in_cabinet + quantity_increase

                    # Informer l'utilisateur de l'ajustement automatique
                    messages.info(
                        request,
                        f"Le nombre de clés dans l'armoire a été automatiquement augmenté de {quantity_increase} "
                        f"pour correspondre à l'augmentation du nombre total d'exemplaires."
                    )

                    # Mettre à jour la variable pour le calcul de cohérence ci-dessous
                    new_in_cabinet = key_type.in_cabinet

                # Print for debugging
                print(
                    f"Après validation - total: {new_total_quantity}, in_cabinet: {new_in_cabinet}, in_safe: {new_in_safe}")

                # Obtenir le nombre d'instances attribuées (qui ne doivent pas être supprimées)
                assigned_count = KeyInstance.objects.filter(
                    key_type=key_type, is_available=False).count()

                # S'assurer que les quantités sont cohérentes
                storage_total = new_in_cabinet + new_in_safe

                # Vérifier si le nouveau total est suffisant pour couvrir les attributions existantes
                if storage_total + assigned_count != new_total_quantity:
                    # Ajuster le total pour qu'il soit cohérent
                    key_type.total_quantity = storage_total + assigned_count
                    messages.warning(request,
                                     f"Le total a été ajusté pour être cohérent avec la somme des exemplaires "
                                     f"(armoire: {new_in_cabinet}, coffre: {new_in_safe}, attribués: {assigned_count}).")

                # Enregistrer les modifications
                key_type.save()

                # Supprimer les instances non attribuées existantes
                # Important: Ne supprimez que les instances disponibles (is_available=True)
                KeyInstance.objects.filter(
                    key_type=key_type, is_available=True).delete()

                # Créer les nouvelles instances dans l'armoire
                cabinet_instances = []
                for i in range(key_type.in_cabinet):
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
                for i in range(key_type.in_safe):
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
    return render(request, 'listings/attribute.html', {'users': User.objects.all().order_by('name', 'firstname'), 'form': form})


def teams(request):
    teams = Team.objects.all().order_by('name')
    return render(request, 'listings/teams.html', {'teams': teams})


@login_required
def user_keys_view(request):
    # Récupérer les paramètres depuis la requête
    user_id = request.GET.get('user_id', None)
    team_id = request.GET.get('team_id', None)

    # Initialiser les variables
    assigned_key_instances = []
    available_key_instances = []
    selected_user = None
    users = []

    # Récupérer toutes les équipes pour les filtres
    teams = Team.objects.all().order_by('name')

    # Filtrer par équipe si une équipe est sélectionnée
    if team_id:
        team = get_object_or_404(Team, id=team_id)
        # Filtrer les utilisateurs par équipe
        users = User.objects.filter(team=team).order_by('name', 'firstname')
    else:
        # Si aucune équipe n'est sélectionnée, ne pas montrer d'utilisateurs
        users = []

    # Filtrer les clés attribuées par utilisateur si un utilisateur est sélectionné
    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        # Récupérer les instances de clés attribuées à cet utilisateur
        assignments = KeyAssignment.objects.filter(
            user=selected_user, is_active=True)
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
        'selected_user': selected_user,
        # L'objet request.user est automatiquement disponible dans les templates
        # grâce au contexte par défaut de Django, donc pas besoin de l'ajouter
    }

    return render(request, 'listings/attribute.html', context)


def get_users_by_team(request, team_id):
    try:
        # Récupérer les membres de l'équipe avec les champs requis
        team_members = User.objects.filter(team_id=team_id).order_by(
            'name', 'firstname').values('id', 'firstname', 'name')

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
        assignment_date_str = data.get('assignment_date')

        # CORRECTION : Convertir la date string en objet date
        if assignment_date_str:
            try:
                # Importer datetime si ce n'est pas déjà fait
                from datetime import datetime
                # Convertir la chaîne en objet date
                assignment_date = datetime.strptime(
                    assignment_date_str, '%Y-%m-%d').date()
            except ValueError:
                # Si le format est incorrect, utiliser la date actuelle
                assignment_date = current_date
        else:
            # Si pas de date fournie, utiliser la date actuelle
            assignment_date = current_date

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
                        assigned_date=assignment_date,  # Maintenant c'est un objet date
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
            # Assurer que assigned_date est bien un objet date
            if assignment.assigned_date:
                formatted_date = assignment.assigned_date.strftime('%d/%m/%Y')
            else:
                formatted_date = None

            updated_keys.append({
                'id': assignment.key_instance.id,
                'number': assignment.key_instance.key_type.number,
                'name': assignment.key_instance.key_type.name,
                'place': assignment.key_instance.key_type.place,
                'location': assignment.key_instance.location,
                'formatted_date': formatted_date,
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur dans assign_keys: {str(e)}", exc_info=True)

        return JsonResponse({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=500)


def user_list(request):
    # Récupérer tous les utilisateurs avec leurs équipes
    users = User.objects.select_related(
        'team').all().order_by('name', 'firstname')
    teams = Team.objects.all().order_by('name')
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
    users = User.objects.all().order_by('name', 'firstname')

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
    users = User.objects.select_related(
        'team').all().order_by('name', 'firstname')
    teams = Team.objects.all().order_by('name')
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


def login_view(request):
    """
    Vue pour gérer la connexion des utilisateurs.
    Authentifie l'utilisateur et crée une session s'il existe.
    """
    # Redirection si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Utilisez le formulaire pour valider les données
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)

            # Tentative d'authentification avec username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Connexion réussie
                login(request, user)

                # Gestion de l'option "Se souvenir de moi"
                if not remember_me:
                    # La session expire à la fermeture du navigateur
                    request.session.set_expiry(0)

                messages.success(
                    request, f'Bienvenue, {user.first_name} {user.last_name}!')

                # Redirection vers la page demandée ou la page d'accueil
                next_url = request.POST.get('next', 'home')
                return redirect(next_url)
        else:
            # Le formulaire n'est pas valide, les erreurs seront affichées dans le template
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    else:
        # Initialiser un formulaire vide pour une requête GET
        form = CustomAuthenticationForm()

    # Passer le formulaire au contexte
    return render(request, 'listings/login.html', {'form': form})


def register_view(request):
    """
    Vue pour gérer l'inscription de nouveaux utilisateurs.
    Crée un nouveau compte avec le rôle 'visiteur' par défaut.
    """
    # Redirection si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Traitement du formulaire soumis
        form = OwnerCreationForm(request.POST)
        if form.is_valid():
            # Création du compte avec le rôle par défaut
            owner = form.save(commit=False)
            owner.role = 'visitor'  # Rôle par défaut: visiteur
            owner.save()

            # Rediriger vers la page de succès au lieu de l'accueil
            return redirect('register_success')  # URL à définir dans urls.py
        else:
            # Affichage des erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Affichage du formulaire vide (GET)
        form = OwnerCreationForm()

    return render(request, 'listings/register.html', {'form': form})


def register_success_view(request):
    """
    Vue pour afficher la page de succès après création de compte
    """
    return render(request, 'listings/success.html')


def logout_view(request):
    """
    Vue pour déconnecter l'utilisateur et détruire sa session.
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')


@login_required
def profile_view(request):
    """
    Vue pour afficher et modifier les informations du profil utilisateur.
    """
    # Initialiser les formulaires avec l'instance de l'utilisateur connecté
    form = OwnerUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(
        user=request.user)  # Le paramètre user est important!

    if request.method == 'POST':
        # Vérifier quel formulaire a été soumis
        if 'update_profile' in request.POST:
            # Traitement du formulaire de mise à jour du profil
            form = OwnerUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Vos informations ont été mises à jour avec succès.')
                return redirect('profile')

        elif 'change_password' in request.POST:
            # Traitement du formulaire de changement de mot de passe
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Mettre à jour la session pour éviter la déconnexion
                update_session_auth_hash(request, password_form.user)
                messages.success(
                    request, 'Votre mot de passe a été modifié avec succès.')
                return redirect('profile')

    # Préparer le contexte avec les deux formulaires
    context = {
        'form': form,
        'password_form': password_form,
    }

    return render(request, 'listings/profile.html', context)

# Fonction pour vérifier si l'utilisateur est un administrateur


def is_admin(user):
    """
    Fonction de vérification utilisée par le décorateur @user_passes_test.
    Vérifie si l'utilisateur connecté a le rôle d'administrateur.
    """
    return user.role == 'admin'


def is_editor_or_admin(user):
    """Vérifie si l'utilisateur a le rôle d'éditeur ou d'administrateur."""
    return user.is_authenticated and (user.role == 'editor' or user.role == 'admin')


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def admin_dashboard(request):
    """
    Vue pour le tableau de bord d'administration.
    Accessible uniquement aux utilisateurs avec le rôle 'admin'.
    """
    # Liste de tous les utilisateurs pour l'administration
    users = Owner.objects.all().order_by('last_name', 'first_name')

    return render(request, 'auth/admin_dashboard.html', {
        'users': users
    })

# Vue réservée aux éditeurs et administrateurs


@login_required
@user_passes_test(is_editor_or_admin, login_url='access_denied')
def editor_dashboard(request):
    """
    Vue pour le tableau de bord d'édition.
    Accessible aux utilisateurs avec le rôle 'editor' ou 'admin'.
    """
    return render(request, 'auth/editor_dashboard.html')

# Vue pour la page d'accès refusé


def access_denied(request):
    """
    Vue pour la page d'accès refusé.
    Affichée lorsqu'un utilisateur tente d'accéder à une page sans les permissions nécessaires.
    """
    messages.error(
        request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    return render(request, 'auth/access_denied.html')


@login_required
@user_passes_test(is_admin)
def owner_management(request):
    """
    Vue pour gérer la liste des utilisateurs (administrateurs uniquement).
    Affiche la liste paginée de tous les utilisateurs.
    Nécessite d'être connecté (@login_required) et d'être administrateur (@user_passes_test).
    """
    # Récupération de tous les utilisateurs, triés par nom puis prénom
    owners_list = Owner.objects.all().order_by('last_name', 'first_name')

    # Pagination (10 utilisateurs par page)
    paginator = Paginator(owners_list, 10)
    page_number = request.GET.get('page')
    owners = paginator.get_page(page_number)

    return render(request, 'listings/owner_management.html', {'owners': owners})


@login_required
@user_passes_test(is_admin)
def add_owner(request):
    """
    Vue pour ajouter un nouvel utilisateur (administrateurs uniquement).
    """
    # Si c'est une requête POST, traiter le formulaire
    if request.method == 'POST':
        form = OwnerCreationForm(request.POST)
        if form.is_valid():
            # Enregistrer l'utilisateur
            owner = form.save(commit=False)

            # Définir les attributs supplémentaires
            owner.role = request.POST.get('role', 'visitor')
            owner.is_active = 'is_active' in request.POST

            # Sauvegarder dans la base de données
            owner.save()

            messages.success(
                request, f'Utilisateur {owner.username} créé avec succès.')
            return redirect('owner_management')
        else:
            # Afficher les erreurs
            messages.error(
                request, 'Erreur dans le formulaire. Veuillez corriger les erreurs ci-dessous.')
    else:
        # Pour une requête GET, afficher un formulaire vide
        form = OwnerCreationForm()

    # Rendre le template avec le formulaire
    return render(request, 'listings/add_owner.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def update_owner(request, user_id):
    """
    Vue pour mettre à jour un utilisateur existant (administrateurs uniquement).
    Traite le formulaire de modification et applique les changements.
    """
    try:
        # Récupération de l'utilisateur à modifier
        user_obj = Owner.objects.get(id=user_id)
    except Owner.DoesNotExist:
        messages.error(request, "Cet utilisateur n'existe pas.")
        # ou 'user_management' selon votre URL
        return redirect('owner_management')

    if request.method == 'POST':
        # Création du formulaire avec les données soumises
        form = OwnerUpdateForm(request.POST, instance=user_obj)

        if form.is_valid():
            # Sauvegarde des modifications du formulaire
            owner = form.save(commit=False)

            # Mise à jour du rôle et du statut actif (qui ne sont pas dans le formulaire)
            owner.role = request.POST.get('role')
            owner.is_active = 'is_active' in request.POST

            # Sauvegarde des modifications
            owner.save()

            messages.success(
                request, f'Utilisateur {owner.username} mis à jour avec succès.')
            # ou 'user_management' selon votre URL
            return redirect('owner_management')
    else:
        # Création du formulaire avec les données de l'utilisateur
        form = OwnerUpdateForm(instance=user_obj)

    # Rendu du template avec le formulaire
    return render(request, 'listings/edit_owner.html', {
        'form': form,
        'user_obj': user_obj  # Utilisation de user_obj comme dans le template
    })


@login_required
@user_passes_test(is_admin)
def delete_owner(request, user_id=None):  # Ajout du paramètre user_id
    """
    Vue pour supprimer un utilisateur (administrateurs uniquement).
    Vérifie que l'administrateur ne supprime pas son propre compte.
    """
    # Pour les requêtes GET, afficher une page de confirmation
    if request.method == 'GET' and user_id:
        try:
            owner = Owner.objects.get(id=user_id)
            return render(request, 'listings/delete_owner_confirm.html', {'owner': owner})
        except Owner.DoesNotExist:
            messages.error(request, "Cet utilisateur n'existe pas.")
            return redirect('owner_management')

    # Pour les requêtes POST, procéder à la suppression
    if request.method == 'POST':
        # Utiliser user_id s'il est fourni
        owner_id = request.POST.get('owner_id') or user_id

        # Vérifier que l'utilisateur ne se supprime pas lui-même
        if int(owner_id) == request.user.id:
            messages.error(
                request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect('owner_management')

        try:
            # Suppression de l'utilisateur
            owner = Owner.objects.get(id=owner_id)
            username = owner.username
            owner.delete()

            messages.success(
                request, f'Utilisateur {username} supprimé avec succès.')
        except Owner.DoesNotExist:
            messages.error(request, "Cet utilisateur n'existe pas.")
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    # Redirection vers la page de gestion des utilisateurs
    return redirect('owner_management')


def is_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'admin'


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def history_view(request):
    """Vue principale pour l'historique des actions - ACCÈS RÉSERVÉ AUX ADMINISTRATEURS"""
    # Récupérer les paramètres de filtrage
    action_type = request.GET.get('action_type', '')
    object_type = request.GET.get('object_type', '')
    user_filter = request.GET.get('user_filter', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    # Construire la requête de base
    actions = ActionLog.objects.all()

    # Filtrer par type d'action
    if action_type:
        actions = actions.filter(action_type=action_type)

    # Filtrer par type d'objet
    if object_type:
        actions = actions.filter(object_type=object_type)

    # Filtrer par utilisateur
    if user_filter:
        actions = actions.filter(user_name__icontains=user_filter)

    # Filtrer par date
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            actions = actions.filter(date_only__gte=date_from_parsed)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            actions = actions.filter(date_only__lte=date_to_parsed)
        except ValueError:
            pass

    # Recherche textuelle
    if search:
        actions = actions.filter(
            Q(description__icontains=search) |
            Q(object_name__icontains=search) |
            Q(user_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(actions, 50)  # 50 actions par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiques rapides
    total_actions = actions.count()
    today_actions = actions.filter(date_only=timezone.now().date()).count()
    week_actions = actions.filter(
        date_only__gte=timezone.now().date() - timedelta(days=7)).count()

    # Récupérer les choix pour les filtres
    action_choices = ActionLog.ACTION_TYPES
    object_choices = ActionLog.OBJECT_TYPES

    context = {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'object_choices': object_choices,
        'total_actions': total_actions,
        'today_actions': today_actions,
        'week_actions': week_actions,
        'current_filters': {
            'action_type': action_type,
            'object_type': object_type,
            'user_filter': user_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }

    return render(request, 'listings/history.html', context)


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def history_detail_view(request, action_id):
    """Vue détaillée pour une action spécifique - ACCÈS RÉSERVÉ AUX ADMINISTRATEURS"""
    action = get_object_or_404(ActionLog, id=action_id)

    # Récupérer les actions liées (même utilisateur, même période)
    related_actions = ActionLog.objects.filter(
        user=action.user,
        timestamp__date=action.timestamp.date()
    ).exclude(id=action.id).order_by('-timestamp')[:10]

    context = {
        'action': action,
        'old_values': action.get_old_values_dict(),
        'new_values': action.get_new_values_dict(),
        'related_actions': related_actions,
    }

    return render(request, 'listings/history_detail.html', context)


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def history_stats_view(request):
    """Vue pour les statistiques de l'historique - ACCÈS RÉSERVÉ AUX ADMINISTRATEURS"""
    # Statistiques par type d'action
    action_stats = ActionLog.objects.values('action_type').annotate(
        count=Count('id')).order_by('-count')

    # Statistiques par type d'objet
    object_stats = ActionLog.objects.values('object_type').annotate(
        count=Count('id')).order_by('-count')

    # Statistiques par utilisateur (top 10)
    user_stats = ActionLog.objects.values('user_name', 'user_role').annotate(
        count=Count('id')).order_by('-count')[:10]

    # Activité par jour (derniers 30 jours)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    daily_activity = ActionLog.objects.filter(
        date_only__gte=thirty_days_ago
    ).values('date_only').annotate(count=Count('id')).order_by('date_only')

    # Convertir les statistiques d'actions en format lisible
    action_stats_readable = []
    for stat in action_stats:
        readable_name = dict(ActionLog.ACTION_TYPES).get(
            stat['action_type'], stat['action_type'])
        action_stats_readable.append({
            'name': readable_name,
            'count': stat['count']
        })

    # Convertir les statistiques d'objets en format lisible
    object_stats_readable = []
    for stat in object_stats:
        readable_name = dict(ActionLog.OBJECT_TYPES).get(
            stat['object_type'], stat['object_type'])
        object_stats_readable.append({
            'name': readable_name,
            'count': stat['count']
        })

    context = {
        'action_stats': action_stats_readable,
        'object_stats': object_stats_readable,
        'user_stats': user_stats,
        'daily_activity': daily_activity,
        'total_actions': ActionLog.objects.count(),
    }

    return render(request, 'listings/history_stats.html', context)


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def export_history_csv(request):
    """Exporte l'historique en CSV - ACCÈS RÉSERVÉ AUX ADMINISTRATEURS"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="historique_actions.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Date et Heure',
        'Date',
        'Heure',
        'Utilisateur',
        'Rôle Utilisateur',
        'Action',
        'Type d\'objet',
        'Objet',
        'Description',
        'Anciennes valeurs',
        'Nouvelles valeurs'
    ])

    # Appliquer les mêmes filtres que la vue principale
    actions = ActionLog.objects.all()

    # Filtres de la requête
    action_type = request.GET.get('action_type', '')
    object_type = request.GET.get('object_type', '')
    user_filter = request.GET.get('user_filter', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    if action_type:
        actions = actions.filter(action_type=action_type)
    if object_type:
        actions = actions.filter(object_type=object_type)
    if user_filter:
        actions = actions.filter(user_name__icontains=user_filter)
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            actions = actions.filter(date_only__gte=date_from_parsed)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            actions = actions.filter(date_only__lte=date_to_parsed)
        except ValueError:
            pass
    if search:
        actions = actions.filter(
            Q(description__icontains=search) |
            Q(object_name__icontains=search) |
            Q(user_name__icontains=search)
        )

    for action in actions:
        old_values_str = ""
        new_values_str = ""

        if action.old_values:
            try:
                old_dict = action.get_old_values_dict()
                old_values_str = " | ".join(
                    [f"{k}: {v}" for k, v in old_dict.items()])
            except:
                old_values_str = action.old_values

        if action.new_values:
            try:
                new_dict = action.get_new_values_dict()
                new_values_str = " | ".join(
                    [f"{k}: {v}" for k, v in new_dict.items()])
            except:
                new_values_str = action.new_values

        writer.writerow([
            action.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            action.timestamp.strftime('%d/%m/%Y'),
            action.timestamp.strftime('%H:%M:%S'),
            action.user_name,
            action.user_role,
            action.get_action_type_display(),
            action.get_object_type_display(),
            action.object_name,
            action.description,
            old_values_str,
            new_values_str
        ])

    return response


@login_required
@user_passes_test(is_admin, login_url='access_denied')
def history_api_search(request):
    """API pour la recherche en temps réel dans l'historique"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    actions = ActionLog.objects.filter(
        Q(description__icontains=query) |
        Q(object_name__icontains=query) |
        Q(user_name__icontains=query)
    )[:20]

    results = []
    for action in actions:
        results.append({
            'id': action.id,
            'timestamp': action.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            'user_name': action.user_name,
            'action_type': action.get_action_type_display(),
            'object_name': action.object_name,
            'description': action.description
        })

    return JsonResponse({'results': results})
