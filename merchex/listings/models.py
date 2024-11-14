from django.db import models

# Create your models here.

# listings/models.py

class Team(models.Model):
    name = models.CharField(max_length=20)  # Assurez-vous que le nom est unique

    def __str__(self):
        return str(self.name)


class Key(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100, default='')
    initial_key_number = models.CharField(max_length=100, default='', null=True, blank=True)
    key_used = models.IntegerField(default=0, blank=True, null=True) 
    key_available = models.CharField(max_length=100, default='', null=True, blank=True)
    in_cabinet = models.BooleanField(default=False)
    in_safe = models.CharField(max_length=100, default='', null=True, blank=True)
    comments = models.CharField(max_length=200, default='', blank=True)
    is_assigned = models.BooleanField(default=False)
    assigned_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='keys')

    def __str__(self):
        assigned_to = f"Attribuée à: {self.assigned_user}" if self.assigned_user else "Non attribuée"
        return f"Clé {self.number}: {self.name}, Emplacement: {self.place}, {assigned_to}"


class User(models.Model):
    firstname = models.CharField(max_length=15)
    name = models.CharField(max_length=15)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    comment = models.CharField(max_length=200, default='', blank=True)  # Champ "commentaire" de TeamMember

    def __str__(self):
        return f"{self.firstname} {self.name} | Team: {self.team.name if self.team else 'No team'}"
