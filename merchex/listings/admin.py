from django.contrib import admin
from .models import User, Team, Key

class UserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'name', 'team', 'comment', 'get_keys_non_assigned','get_keys_assigned')
    list_filter = ('team',)
    search_fields = ('firstname', 'name')

    def get_keys_non_assigned(self, obj):
        """Affiche les clés non attribuées à cet utilisateur."""
        non_assigned_keys = Key.objects.filter(assigned_user__isnull=True)
        return ", ".join([str(key) for key in non_assigned_keys])
    get_keys_non_assigned.short_description = 'Clés non assignées'
    
    def get_keys_assigned(self, obj):
        """Affiche les clés assignées à cet utilisateur."""
        assigned_keys = Key.objects.filter(assigned_user=obj)
        return ", ".join([str(key) for key in assigned_keys])
    get_keys_assigned.short_description = 'Clés assignées'


class KeyAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'place', 'key_used', 'get_user')
    search_fields = ('name', 'number')

    def get_user(self, obj):
        """Affiche l'utilisateur assigné à la clé."""
        return obj.assigned_user.name if obj.assigned_user else 'Aucun utilisateur attribué'
    get_user.short_description = 'Utilisateur Assigné'


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Enregistrement des modèles dans l'interface d'administration
admin.site.register(User, UserAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Team, TeamAdmin)
