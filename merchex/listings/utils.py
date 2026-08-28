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



def _en_json(donnees):
    """
    Serialise les valeurs d'une action pour l'historique.

    `default=str` ne rattrape que les VALEURS non serialisables, jamais les
    CLES : un dictionnaire dont une cle n'est pas une chaine fait echouer
    json.dumps, et l'action passe alors a la trappe. On force donc les cles
    en texte avant de serialiser.
    """
    if isinstance(donnees, dict):
        donnees = {str(cle): valeur for cle, valeur in donnees.items()}
    return json.dumps(donnees, ensure_ascii=False, default=str)


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
            old_values_json = _en_json(old_values)
        if new_values:
            new_values_json = _en_json(new_values)
        if affected_users:
            affected_users_json = _en_json(affected_users)

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
        # On n'echoue pas l'operation metier pour un probleme de journal, mais
        # la trace complete est indispensable : c'est ce silence qui a laisse
        # les actions sur les comptes disparaitre de l'historique sans alerte.
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(
            "Action NON journalisee (%s %s id=%s) : %s",
            action_type, object_type, object_id, e)

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
                # str() est indispensable : sur Owner, qui herite d'AbstractUser,
                # les verbose_name de Django sont des traductions paresseuses.
                # Telles quelles, elles font echouer json.dumps ("keys must be
                # str, ... not __proxy__") et l'action n'est jamais journalisee.
                cle = str(field.verbose_name or field.name)
                if value is None:
                    fields_dict[cle] = None
                elif hasattr(value, 'name'):
                    fields_dict[cle] = value.name
                elif hasattr(value, '__str__'):
                    fields_dict[cle] = str(value)
                else:
                    fields_dict[cle] = value
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
