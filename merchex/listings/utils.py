# ================================
# UTILITAIRES POUR L'HISTORIQUE (listings/utils.py)
# ================================

import json
from django.utils import timezone
from threading import local

# Thread local storage pour l'utilisateur courant
_thread_locals = local()


def get_current_user():
    """Récupère l'utilisateur courant depuis le thread local"""
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """Définit l'utilisateur courant dans le thread local"""
    _thread_locals.user = user


def log_action(user, action_type, object_type, object_id, object_name, description,
               old_values=None, new_values=None, affected_users=None):
    """
    Fonction utilitaire pour enregistrer une action dans l'historique
    """
    try:
        # Import tardif pour éviter les problèmes de dépendances circulaires
        from .models import ActionLog

        # Utiliser l'utilisateur passé en paramètre ou celui du thread local
        if user is None:
            user = get_current_user()

        # Convertir les dictionnaires en JSON si nécessaire
        old_values_json = None
        new_values_json = None
        affected_users_json = None

        if old_values:
            old_values_json = json.dumps(
                old_values, ensure_ascii=False, default=str)
        if new_values:
            new_values_json = json.dumps(
                new_values, ensure_ascii=False, default=str)
        if affected_users:
            affected_users_json = json.dumps(
                affected_users, ensure_ascii=False, default=str)

        # Nom et rôle de l'utilisateur
        user_name = "Système"
        user_role = "system"

        if user and hasattr(user, 'get_full_name'):
            user_name = user.get_full_name() or user.username
            user_role = getattr(user, 'role', 'visitor')
        elif user:
            user_name = str(user)
            user_role = getattr(user, 'role', 'visitor')

        # Créer l'entrée dans le journal
        ActionLog.objects.create(
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            object_name=object_name,
            user=user,
            user_name=user_name,
            user_role=user_role,
            description=description,
            old_values=old_values_json,
            new_values=new_values_json,
            affected_users=affected_users_json,
        )

    except Exception as e:
        # En cas d'erreur, logger l'exception mais ne pas faire échouer l'opération principale
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Erreur lors de l'enregistrement de l'action dans l'historique: {str(e)}")
        logger.error(
            f"Action: {action_type}, Object: {object_type}, ID: {object_id}")

        # Optionnel : vous pouvez aussi utiliser Django messages pour informer l'utilisateur
        # from django.contrib import messages
        # if user and hasattr(user, '_messages'):
        #     messages.warning(user, "L'action a été effectuée mais n'a pas pu être enregistrée dans l'historique.")


def log_action(user, action_type, object_type, object_id, object_name, description,
               old_values=None, new_values=None, affected_users=None):
    """
    Fonction utilitaire pour enregistrer une action dans l'historique
    """
    try:
        # Import tardif pour éviter les problèmes de dépendances circulaires
        from .models import ActionLog

        # Utiliser l'utilisateur passé en paramètre ou celui du thread local
        if user is None:
            user = get_current_user()

        # Convertir les dictionnaires en JSON si nécessaire
        old_values_json = None
        new_values_json = None
        affected_users_json = None

        if old_values:
            old_values_json = json.dumps(
                old_values, ensure_ascii=False, default=str)
        if new_values:
            new_values_json = json.dumps(
                new_values, ensure_ascii=False, default=str)
        if affected_users:
            affected_users_json = json.dumps(
                affected_users, ensure_ascii=False, default=str)

        # Nom et rôle de l'utilisateur
        user_name = "Système"
        user_role = "system"

        if user and hasattr(user, 'get_full_name'):
            user_name = user.get_full_name() or user.username
            user_role = getattr(user, 'role', 'visitor')
        elif user:
            user_name = str(user)
            user_role = getattr(user, 'role', 'visitor')

        # Créer l'entrée dans le journal
        ActionLog.objects.create(
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            object_name=object_name,
            user=user,
            user_name=user_name,
            user_role=user_role,
            description=description,
            old_values=old_values_json,
            new_values=new_values_json,
            affected_users=affected_users_json,
        )

    except Exception as e:
        # En cas d'erreur, logger l'exception mais ne pas faire échouer l'opération principale
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Erreur lors de l'enregistrement de l'action dans l'historique: {str(e)}")
        logger.error(
            f"Action: {action_type}, Object: {object_type}, ID: {object_id}")

        # Optionnel : vous pouvez aussi utiliser Django messages pour informer l'utilisateur
        # from django.contrib import messages
        # if user and hasattr(user, '_messages'):
        #     messages.warning(user, "L'action a été effectuée mais n'a pas pu être enregistrée dans l'historique.")


def get_object_representation(obj):
    """
    Retourne une représentation lisible d'un objet pour l'historique
    """
    if hasattr(obj, 'name'):
        return obj.name
    elif hasattr(obj, 'firstname') and hasattr(obj, 'name'):
        return f"{obj.firstname} {obj.name}"
    elif hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
        return f"{obj.first_name} {obj.last_name}"
    elif hasattr(obj, 'username'):
        return obj.username
    elif hasattr(obj, 'number'):
        return f"Clé #{obj.number}"
    elif hasattr(obj, 'key_type') and hasattr(obj.key_type, 'number'):
        return f"Instance de clé #{obj.key_type.number}"
    else:
        return str(obj)


def get_model_fields_dict(instance, exclude_fields=None):
    """
    Retourne un dictionnaire avec les valeurs des champs du modèle
    """
    if exclude_fields is None:
        exclude_fields = ['id', 'password', 'last_login',
                          'date_joined', 'created_at', 'updated_at']

    fields_dict = {}
    for field in instance._meta.fields:
        if field.name not in exclude_fields:
            try:
                value = getattr(instance, field.name)
                if value is None:
                    fields_dict[field.verbose_name or field.name] = None
                elif hasattr(value, 'name'):
                    fields_dict[field.verbose_name or field.name] = value.name
                elif hasattr(value, '__str__'):
                    fields_dict[field.verbose_name or field.name] = str(value)
                else:
                    fields_dict[field.verbose_name or field.name] = value
            except Exception:
                # Si on ne peut pas récupérer la valeur, on l'ignore
                continue

    return fields_dict


def get_changes_description(old_values, new_values):
    """
    Génère une description des changements entre anciennes et nouvelles valeurs
    """
    if not old_values or not new_values:
        return ""

    changes = []
    for key, new_value in new_values.items():
        old_value = old_values.get(key)
        if old_value != new_value:
            changes.append(f"{key}: '{old_value}' → '{new_value}'")

    return " | ".join(changes)

# ================================
# FONCTIONS POUR LES ACTIONS PERSONNALISÉES
# ================================


def log_bulk_delete(user, object_type, deleted_objects, description):
    """
    Enregistre les suppressions en masse
    """
    affected_objects = [get_object_representation(
        obj) for obj in deleted_objects]

    log_action(
        user=user,
        action_type='BULK_DELETE',
        object_type=object_type,
        object_id=None,
        object_name=f"{len(deleted_objects)} éléments",
        description=description,
        affected_users=affected_objects
    )


def log_password_change(user, target_user=None):
    """
    Enregistre les changements de mot de passe
    """
    if target_user is None:
        target_user = user

    log_action(
        user=user,
        action_type='PASSWORD_CHANGE',
        object_type='OWNER',
        object_id=target_user.id,
        object_name=get_object_representation(target_user),
        description=f"Changement de mot de passe pour {get_object_representation(target_user)}"
    )


def log_password_reset(user_email):
    """
    Enregistre les demandes de réinitialisation de mot de passe
    """
    log_action(
        user=None,
        action_type='PASSWORD_RESET',
        object_type='SYSTEM',
        object_id=None,
        object_name=user_email,
        description=f"Demande de réinitialisation de mot de passe pour {user_email}"
    )

# ================================
# MIDDLEWARE POUR CAPTURER L'UTILISATEUR COURANT
# ================================


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

    def get_object_representation(obj):
        if obj is None:
            return "Non défini"

        if hasattr(obj, 'name') and obj.name:
            return obj.name
        elif hasattr(obj, 'firstname') and hasattr(obj, 'name'):
            return f"{obj.firstname} {obj.name}"
        elif hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            return f"{obj.first_name} {obj.last_name}"
        elif hasattr(obj, 'username') and obj.username:
            return obj.username
        elif hasattr(obj, 'number'):
            return f"Clé #{obj.number}"
        elif hasattr(obj, 'key_type') and hasattr(obj.key_type, 'number'):
            return f"Instance de clé #{obj.key_type.number}"
        else:
            return str(obj)

    def get_model_fields_dict(instance, exclude_fields=None):
        """
        Retourne un dictionnaire avec les valeurs des champs du modèle
        """
        if exclude_fields is None:
            exclude_fields = ['id', 'password', 'last_login',
                              'date_joined', 'created_at', 'updated_at']

        fields_dict = {}
        for field in instance._meta.fields:
            if field.name not in exclude_fields:
                try:
                    value = getattr(instance, field.name)
                    field_name = field.verbose_name or field.name

                    if value is None:
                        fields_dict[field_name] = None
                    elif hasattr(field, 'related_model'):
                        # C'est une relation (ForeignKey, OneToOne, etc.)
                        if value:
                            fields_dict[field_name] = get_object_representation(
                                value)
                        else:
                            fields_dict[field_name] = None
                    else:
                        # Champ normal
                        fields_dict[field_name] = str(value)
                except Exception as e:
                    # Si on ne peut pas récupérer la valeur, on l'ignore
                    print(
                        f"Erreur lors de la récupération du champ {field.name}: {e}")
                    continue

        return fields_dict
