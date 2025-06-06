# ================================
# 4. SIGNAUX POUR CAPTURER LES ACTIONS (signals.py)
# ================================

from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import KeyType, KeyInstance, KeyAssignment, User, Team, Owner, ActionLog
from .utils import log_action, get_object_representation, get_model_fields_dict, get_current_user, get_changes_description

# Variables globales pour stocker les anciennes valeurs
_old_values = {}

# ================================
# SIGNAUX POUR LES CONNEXIONS/DÉCONNEXIONS
# ================================


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Enregistre les connexions utilisateur"""
    log_action(
        user=user,
        action_type='LOGIN',
        object_type='SYSTEM',
        object_id=user.id,
        object_name=get_object_representation(user),
        description=f"Connexion de l'utilisateur {get_object_representation(user)} (rôle: {getattr(user, 'role', 'inconnu')})"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Enregistre les déconnexions utilisateur"""
    if user and user.is_authenticated:
        log_action(
            user=user,
            action_type='LOGOUT',
            object_type='SYSTEM',
            object_id=user.id,
            object_name=get_object_representation(user),
            description=f"Déconnexion de l'utilisateur {get_object_representation(user)}"
        )

# ================================
# SIGNAUX POUR LES TYPES DE CLÉS
# ================================


@receiver(pre_save, sender=KeyType)
def capture_keytype_old_values(sender, instance, **kwargs):
    """Capture les anciennes valeurs avant modification"""
    if instance.pk:
        try:
            old_instance = KeyType.objects.get(pk=instance.pk)
            _old_values[f"keytype_{instance.id}"] = get_model_fields_dict(
                old_instance)
        except KeyType.DoesNotExist:
            pass


@receiver(post_save, sender=KeyType)
def log_keytype_save(sender, instance, created, **kwargs):
    """Enregistre la création/modification des types de clés"""
    current_user = get_current_user()

    if created:
        log_action(
            user=current_user,
            action_type='CREATE',
            object_type='KEYTYPE',
            object_id=instance.id,
            object_name=get_object_representation(instance),
            description=f"Création du type de clé #{instance.number} : {instance.name} (total: {instance.total_quantity}, armoire: {instance.in_cabinet}, coffre: {instance.in_safe})",
            new_values=get_model_fields_dict(instance)
        )
    else:
        old_values = _old_values.get(f"keytype_{instance.id}", {})
        new_values = get_model_fields_dict(instance)

        if old_values != new_values:
            changes_desc = get_changes_description(old_values, new_values)
            log_action(
                user=current_user,
                action_type='UPDATE',
                object_type='KEYTYPE',
                object_id=instance.id,
                object_name=get_object_representation(instance),
                description=f"Modification du type de clé #{instance.number} : {instance.name}. Changements: {changes_desc}",
                old_values=old_values,
                new_values=new_values
            )


@receiver(pre_delete, sender=KeyType)
def capture_keytype_before_delete(sender, instance, **kwargs):
    """Capture les informations avant suppression"""
    _old_values[f"keytype_delete_{instance.id}"] = get_model_fields_dict(
        instance)


@receiver(post_delete, sender=KeyType)
def log_keytype_delete(sender, instance, **kwargs):
    """Enregistre la suppression des types de clés"""
    current_user = get_current_user()
    old_values = _old_values.get(f"keytype_delete_{instance.id}", {})

    log_action(
        user=current_user,
        action_type='DELETE',
        object_type='KEYTYPE',
        object_id=instance.id,
        object_name=get_object_representation(instance),
        description=f"Suppression du type de clé #{instance.number} : {instance.name}",
        old_values=old_values
    )

# ================================
# SIGNAUX POUR LES UTILISATEURS
# ================================


@receiver(pre_save, sender=User)
def capture_user_old_values(sender, instance, **kwargs):
    """Capture les anciennes valeurs avant modification"""
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            _old_values[f"user_{instance.id}"] = get_model_fields_dict(
                old_instance)
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    """Enregistre la création/modification des utilisateurs"""
    current_user = get_current_user()

    if created:
        log_action(
            user=current_user,
            action_type='CREATE',
            object_type='USER',
            object_id=instance.id,
            object_name=get_object_representation(instance),
            description=f"Création de l'utilisateur : {get_object_representation(instance)} (équipe: {instance.team.name if instance.team else 'Aucune'})",
            new_values=get_model_fields_dict(instance)
        )
    else:
        old_values = _old_values.get(f"user_{instance.id}", {})
        new_values = get_model_fields_dict(instance)

        if old_values != new_values:
            changes_desc = get_changes_description(old_values, new_values)
            log_action(
                user=current_user,
                action_type='UPDATE',
                object_type='USER',
                object_id=instance.id,
                object_name=get_object_representation(instance),
                description=f"Modification de l'utilisateur : {get_object_representation(instance)}. Changements: {changes_desc}",
                old_values=old_values,
                new_values=new_values
            )


@receiver(pre_delete, sender=User)
def capture_user_before_delete(sender, instance, **kwargs):
    """Capture les informations avant suppression"""
    _old_values[f"user_delete_{instance.id}"] = get_model_fields_dict(instance)


@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    """Enregistre la suppression des utilisateurs"""
    current_user = get_current_user()
    old_values = _old_values.get(f"user_delete_{instance.id}", {})

    log_action(
        user=current_user,
        action_type='DELETE',
        object_type='USER',
        object_id=instance.id,
        object_name=get_object_representation(instance),
        description=f"Suppression de l'utilisateur : {get_object_representation(instance)}",
        old_values=old_values
    )

# ================================
# SIGNAUX POUR LES ÉQUIPES
# ================================


@receiver(pre_save, sender=Team)
def capture_team_old_values(sender, instance, **kwargs):
    """Capture les anciennes valeurs avant modification"""
    if instance.pk:
        try:
            old_instance = Team.objects.get(pk=instance.pk)
            _old_values[f"team_{instance.id}"] = get_model_fields_dict(
                old_instance)
        except Team.DoesNotExist:
            pass


@receiver(post_save, sender=Team)
def log_team_save(sender, instance, created, **kwargs):
    """Enregistre la création/modification des équipes"""
    current_user = get_current_user()

    if created:
        log_action(
            user=current_user,
            action_type='CREATE',
            object_type='TEAM',
            object_id=instance.id,
            object_name=get_object_representation(instance),
            description=f"Création de l'équipe : {get_object_representation(instance)}",
            new_values=get_model_fields_dict(instance)
        )
    else:
        old_values = _old_values.get(f"team_{instance.id}", {})
        new_values = get_model_fields_dict(instance)

        if old_values != new_values:
            changes_desc = get_changes_description(old_values, new_values)
            log_action(
                user=current_user,
                action_type='UPDATE',
                object_type='TEAM',
                object_id=instance.id,
                object_name=get_object_representation(instance),
                description=f"Modification de l'équipe : {get_object_representation(instance)}. Changements: {changes_desc}",
                old_values=old_values,
                new_values=new_values
            )


@receiver(pre_delete, sender=Team)
def capture_team_before_delete(sender, instance, **kwargs):
    """Capture les informations avant suppression"""
    _old_values[f"team_delete_{instance.id}"] = get_model_fields_dict(instance)


@receiver(post_delete, sender=Team)
def log_team_delete(sender, instance, **kwargs):
    """Enregistre la suppression des équipes"""
    current_user = get_current_user()
    old_values = _old_values.get(f"team_delete_{instance.id}", {})

    log_action(
        user=current_user,
        action_type='DELETE',
        object_type='TEAM',
        object_id=instance.id,
        object_name=get_object_representation(instance),
        description=f"Suppression de l'équipe : {get_object_representation(instance)}",
        old_values=old_values
    )

# ================================
# SIGNAUX POUR LES ATTRIBUTIONS DE CLÉS
# ================================


@receiver(pre_save, sender=KeyAssignment)
def capture_keyassignment_old_values(sender, instance, **kwargs):
    """Capture les anciennes valeurs avant modification"""
    if instance.pk:
        try:
            old_instance = KeyAssignment.objects.get(pk=instance.pk)
            _old_values[f"keyassignment_{instance.id}"] = {
                'is_active': old_instance.is_active,
                'assigned_date': old_instance.assigned_date,
                'return_date': old_instance.return_date,
                'user': get_object_representation(old_instance.user),
                'key_instance': get_object_representation(old_instance.key_instance),
            }
        except KeyAssignment.DoesNotExist:
            pass


@receiver(post_save, sender=KeyAssignment)
def log_keyassignment_save(sender, instance, created, **kwargs):
    """Enregistre les attributions/désattributions de clés"""
    current_user = get_current_user()

    if created:
        log_action(
            user=current_user,
            action_type='ASSIGN',
            object_type='KEYASSIGNMENT',
            object_id=instance.id,
            object_name=f"Clé {get_object_representation(instance.key_instance)} → {get_object_representation(instance.user)}",
            description=f"Attribution de la clé {get_object_representation(instance.key_instance)} à {get_object_representation(instance.user)} le {instance.assigned_date.strftime('%d/%m/%Y') if instance.assigned_date else 'date inconnue'}",
            new_values=get_model_fields_dict(instance),
            affected_users=[get_object_representation(instance.user)]
        )
    else:
        old_values = _old_values.get(f"keyassignment_{instance.id}", {})
        # Vérifier si l'attribution a été désactivée (retour de clé)
        if old_values.get('is_active') and not instance.is_active and instance.return_date:
            log_action(
                user=current_user,
                action_type='UNASSIGN',
                object_type='KEYASSIGNMENT',
                object_id=instance.id,
                object_name=f"Clé {get_object_representation(instance.key_instance)} ← {get_object_representation(instance.user)}",
                description=f"Retour de la clé {get_object_representation(instance.key_instance)} par {get_object_representation(instance.user)} le {instance.return_date.strftime('%d/%m/%Y')}",
                old_values=old_values,
                new_values=get_model_fields_dict(instance),
                affected_users=[get_object_representation(instance.user)]
            )

# ================================
# SIGNAUX POUR LES PROPRIÉTAIRES (Owner)
# ================================


@receiver(pre_save, sender=Owner)
def capture_owner_old_values(sender, instance, **kwargs):
    """Capture les anciennes valeurs avant modification"""
    if instance.pk:
        try:
            old_instance = Owner.objects.get(pk=instance.pk)
            _old_values[f"owner_{instance.id}"] = get_model_fields_dict(
                old_instance)
        except Owner.DoesNotExist:
            pass


@receiver(post_save, sender=Owner)
def log_owner_save(sender, instance, created, **kwargs):
    """Enregistre la création/modification des propriétaires"""
    current_user = get_current_user()

    if created:
        log_action(
            user=current_user,
            action_type='CREATE',
            object_type='OWNER',
            object_id=instance.id,
            object_name=get_object_representation(instance),
            description=f"Création du compte propriétaire : {get_object_representation(instance)} (rôle: {instance.role})",
            new_values=get_model_fields_dict(instance)
        )
    else:
        old_values = _old_values.get(f"owner_{instance.id}", {})
        new_values = get_model_fields_dict(instance)

        if old_values != new_values:
            changes_desc = get_changes_description(old_values, new_values)
            log_action(
                user=current_user,
                action_type='UPDATE',
                object_type='OWNER',
                object_id=instance.id,
                object_name=get_object_representation(instance),
                description=f"Modification du compte propriétaire : {get_object_representation(instance)}. Changements: {changes_desc}",
                old_values=old_values,
                new_values=new_values
            )


@receiver(pre_delete, sender=Owner)
def capture_owner_before_delete(sender, instance, **kwargs):
    """Capture les informations avant suppression"""
    _old_values[f"owner_delete_{instance.id}"] = get_model_fields_dict(
        instance)


@receiver(post_delete, sender=Owner)
def log_owner_delete(sender, instance, **kwargs):
    """Enregistre la suppression des propriétaires"""
    current_user = get_current_user()
    old_values = _old_values.get(f"owner_delete_{instance.id}", {})

    log_action(
        user=current_user,
        action_type='DELETE',
        object_type='OWNER',
        object_id=instance.id,
        object_name=get_object_representation(instance),
        description=f"Suppression du compte propriétaire : {get_object_representation(instance)}",
        old_values=old_values
    )
