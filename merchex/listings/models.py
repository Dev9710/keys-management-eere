from django.db import models
from django.utils import timezone
from django.db.models import Sum


class Team(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class User(models.Model):
    firstname = models.CharField(max_length=15)
    name = models.CharField(max_length=15)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    comment = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return f"{self.firstname} {self.name} | Team: {self.team.name if self.team else 'Aucune équipe'}"


class KeyType(models.Model):
    """Représente un type/modèle spécifique de clé"""
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100, default='')
    total_quantity = models.IntegerField(
        default=1, help_text="Nombre total d'exemplaires de cette clé")
    in_cabinet = models.IntegerField(
        default=0, help_text="Nombre de clés stockées dans l'armoire")
    in_safe = models.IntegerField(
        default=0, help_text="Nombre de clés stockées dans le coffre")
    comments = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return f"Clé {self.number}: {self.name}, Emplacement: {self.place}"

    def save(self, *args, **kwargs):
        """Sauvegarde le type de clé en s'assurant que les modifications sont appliquées
        même en cas de modifications simultanées"""
        # Si c'est une nouvelle instance, pas besoin de vérifications
        if not self.pk:
            return super().save(*args, **kwargs)

        # Pour une mise à jour, vérifier si nous utilisons update_fields
        if 'update_fields' in kwargs and kwargs['update_fields']:
            # Si oui, continuer normalement
            return super().save(*args, **kwargs)

        # Pour une mise à jour complète, s'assurer que les compteurs ne sont pas altérés
        # sauf si explicitement demandé
        try:
            # Obtenir l'instance existante
            old_instance = KeyType.objects.get(pk=self.pk)

            # Si update_fields n'est pas spécifié, préserver certains champs
            # qui pourraient être mis à jour par d'autres processus
            explicitly_updating_cabinet = 'in_cabinet' in kwargs.get(
                'update_fields', [])
            explicitly_updating_safe = 'in_safe' in kwargs.get(
                'update_fields', [])

            # Ne pas écraser les valeurs de compteurs si elles ne sont pas
            # explicitement mises à jour
            if not explicitly_updating_cabinet:
                self.in_cabinet = old_instance.in_cabinet
            if not explicitly_updating_safe:
                self.in_safe = old_instance.in_safe

        except (KeyType.DoesNotExist, Exception):
            # Si l'instance n'existe pas ou une autre erreur, continuer normalement
            pass

        return super().save(*args, **kwargs)

    @property
    def available_quantity(self):
        """Retourne le nombre d'exemplaires disponibles de cette clé"""
        return KeyInstance.objects.filter(
            key_type=self,
            is_available=True
        ).count()

    @property
    def assigned_quantity(self):
        """Retourne le nombre d'exemplaires attribués de cette clé"""
        return KeyInstance.objects.filter(
            key_type=self,
            is_available=False
        ).count()

    @property
    def storage_total(self):
        """Retourne le total des clés en stockage (armoire + coffre)"""
        return self.in_cabinet + self.in_safe

    @property
    def total_quantity_calculated(self):
        """Calcule le nombre total d'exemplaires en additionnant attribués + armoire + coffre"""
        return self.assigned_quantity + self.in_cabinet + self.in_safe

    def verify_quantities(self):
        """Vérifie que le total déclaré correspond à la somme des exemplaires"""
        assigned = self.assigned_quantity
        in_cabinet = self.in_cabinet
        in_safe = self.in_safe

        calculated_total = assigned + in_cabinet + in_safe
        if calculated_total != self.total_quantity:
            return False, f"Incohérence: total déclaré {self.total_quantity} != somme des exemplaires ({assigned} + {in_cabinet} + {in_safe} = {calculated_total})"
        return True, "OK"


class KeyInstance(models.Model):
    """Représente un exemplaire physique individuel d'une clé"""
    key_type = models.ForeignKey(
        KeyType, on_delete=models.CASCADE, related_name='instances')
    serial_number = models.CharField(max_length=50, blank=True, null=True,
                                     help_text="Identifiant unique optionnel pour cet exemplaire spécifique")
    is_available = models.BooleanField(default=True)
    condition = models.CharField(max_length=50, default='Bon',
                                 choices=[('Neuf', 'Neuf'), ('Bon', 'Bon'), ('Moyen', 'Moyen'), ('Mauvais', 'Mauvais')])
    location = models.CharField(max_length=50, default='Cabinet',
                                choices=[('Cabinet', 'Cabinet'), ('Coffre', 'Coffre'), ('Utilisateur', 'Utilisateur')])
    original_location = models.CharField(max_length=50, default='', blank=True,
                                         help_text="Localisation d'origine, pour restaurer après retour")
    comments = models.CharField(max_length=200, default='', blank=True)

    class Meta:
        unique_together = ('key_type', 'serial_number')

    def __str__(self):
        if self.serial_number:
            return f"Clé {self.key_type.number} (copie: {self.serial_number})"
        return f"Clé {self.key_type.number} (copie #{self.id})"

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle instance, enregistrer la localisation d'origine
        if not self.pk and not self.original_location:
            self.original_location = self.location

        # Si c'est une instance existante (mise à jour)
        if self.pk:
            try:
                # Récupérer l'ancienne version de l'instance pour comparaison
                old_instance = KeyInstance.objects.get(pk=self.pk)

                # Important: Vérifier si cette mise à jour n'est pas déjà gérée par KeyAssignment
                if not hasattr(self, 'assignment'):
                    # Si l'état de disponibilité a changé
                    if old_instance.is_available != self.is_available:
                        # Cas 1: La clé passe de disponible à non disponible (attribution manuelle)
                        if old_instance.is_available and not self.is_available:
                            # Enregistrer la localisation d'origine si ce n'est pas déjà fait
                            if not self.original_location:
                                self.original_location = old_instance.location

                            # Décrémenter le compteur approprié selon la localisation d'origine
                            key_type = self.key_type
                            if old_instance.location == 'Cabinet':
                                key_type.in_cabinet = max(
                                    0, key_type.in_cabinet - 1)
                                key_type.save(update_fields=['in_cabinet'])
                            elif old_instance.location == 'Coffre':
                                key_type.in_safe = max(0, key_type.in_safe - 1)
                                key_type.save(update_fields=['in_safe'])

                            # Mettre à jour la localisation à Utilisateur
                            self.location = 'Utilisateur'

                        # Cas 2: La clé passe de non disponible à disponible (retour manuel)
                        elif not old_instance.is_available and self.is_available:
                            # Restaurer la localisation d'origine
                            original_loc = self.original_location or 'Cabinet'
                            self.location = original_loc

                            # Incrémenter le compteur approprié
                            key_type = self.key_type
                            if original_loc == 'Cabinet':
                                key_type.in_cabinet += 1
                                key_type.save(update_fields=['in_cabinet'])
                            elif original_loc == 'Coffre':
                                key_type.in_safe += 1
                                key_type.save(update_fields=['in_safe'])

            except KeyInstance.DoesNotExist:
                pass

        # Mettre à jour la localisation selon la disponibilité
        if self.is_available and self.location == 'Utilisateur':
            # Si la localisation d'origine est connue, l'utiliser
            if self.original_location:
                self.location = self.original_location
            else:
                # Sinon utiliser Cabinet par défaut
                self.location = 'Cabinet'
        elif not self.is_available:
            # Si l'instance n'est pas disponible, sa localisation est Utilisateur
            self.location = 'Utilisateur'

        # Sauvegarder l'instance
        super().save(*args, **kwargs)

    @property
    def is_assigned(self):
        """Vérifie si cette instance de clé est actuellement attribuée"""
        return hasattr(self, 'assignment') and self.assignment.is_active


class KeyAssignment(models.Model):
    key_instance = models.OneToOneField(
        KeyInstance, on_delete=models.CASCADE, related_name='assignment')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='key_assignments')
    assigned_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    comments = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return f"Clé {self.key_instance.key_type.number} assignée à {self.user.firstname} {self.user.name} le {self.assigned_date}"

    def save(self, *args, **kwargs):
        # Stocker l'état actif précédent pour vérifier s'il y a un changement
        was_active = False

        # Pour une instance existante, récupérer l'état précédent
        if self.pk:
            try:
                previous = KeyAssignment.objects.get(pk=self.pk)
                was_active = previous.is_active
            except KeyAssignment.DoesNotExist:
                pass

        # Déterminer si l'état actif a changé
        state_changed = was_active != self.is_active

        # Cas 1: Attribution nouvelle ou réactivation
        if self.is_active and (not self.pk or state_changed):
            # S'assurer que la clé est marquée comme non disponible
            key_instance = self.key_instance

            # Ne modifier la clé que si son état change
            if key_instance.is_available:
                # Stocker la localisation d'origine si nécessaire
                if not key_instance.original_location:
                    key_instance.original_location = key_instance.location

                # Décrémenter le compteur approprié
                key_type = key_instance.key_type
                if key_instance.location == 'Cabinet':
                    key_type.in_cabinet = max(0, key_type.in_cabinet - 1)
                    key_type.save(update_fields=['in_cabinet'])
                elif key_instance.location == 'Coffre':
                    key_type.in_safe = max(0, key_type.in_safe - 1)
                    key_type.save(update_fields=['in_safe'])

                # Mettre à jour la disponibilité et l'emplacement
                key_instance.is_available = False
                key_instance.location = 'Utilisateur'
                key_instance.save()

        # Cas 2: Désactivation d'une attribution (retour de clé)
        elif was_active and not self.is_active:
            key_instance = self.key_instance

            # Ne modifier la clé que si son état change
            if not key_instance.is_available:
                # Restaurer la localisation d'origine
                original_loc = key_instance.original_location or 'Cabinet'
                key_instance.location = original_loc

                # Incrémenter le compteur approprié
                key_type = key_instance.key_type
                if original_loc == 'Cabinet':
                    key_type.in_cabinet += 1
                    key_type.save(update_fields=['in_cabinet'])
                elif original_loc == 'Coffre':
                    key_type.in_safe += 1
                    key_type.save(update_fields=['in_safe'])

                # Mettre à jour la disponibilité
                key_instance.is_available = True
                key_instance.save()

        # Sauvegarder l'attribution
        super().save(*args, **kwargs)
