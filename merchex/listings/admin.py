from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Team, KeyType, KeyInstance, KeyAssignment, Owner

# Inline pour les attributions de clés (uniquement pour User, pas pour Owner)


class KeyAssignmentInline(admin.TabularInline):
    model = KeyAssignment
    extra = 1
    # Ne spécifiez PAS fk_name ici

# Admin pour User (détenteurs de clés)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'name', 'team',
                    'comment', 'get_assigned_keys')
    list_filter = ('team',)
    search_fields = ('firstname', 'name')
    inlines = [KeyAssignmentInline]

    def get_assigned_keys(self, obj):
        """Affiche les clés actuellement assignées à cet utilisateur."""
        assignments = KeyAssignment.objects.filter(user=obj, is_active=True)
        if assignments.exists():
            return ", ".join([f"{a.key_instance.key_type.number}: {a.key_instance.key_type.name}" for a in assignments])
        return "Aucune clé"
    get_assigned_keys.short_description = 'Clés assignées'

# Inline pour les instances de clés


class KeyInstanceInline(admin.TabularInline):
    model = KeyInstance
    extra = 1
    fields = ('serial_number', 'is_available',
              'condition', 'location', 'comments')

# Inline pour les attributions de clés depuis la perspective de KeyInstance


class KeyAssignmentInstanceInline(admin.TabularInline):
    model = KeyAssignment
    extra = 0
    fields = ('user', 'assigned_date', 'return_date', 'is_active', 'comments')
    readonly_fields = ('user', 'assigned_date')

# Admin pour les types de clés


@admin.register(KeyType)
class KeyTypeAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'place', 'total_quantity',
                    'in_cabinet', 'in_safe', 'assigned_quantity', 'check_consistency')
    search_fields = ('name', 'number', 'place')
    list_filter = ('place',)
    inlines = [KeyInstanceInline]

    def assigned_quantity(self, obj):
        return obj.assigned_quantity
    assigned_quantity.short_description = 'Exemplaires attribués'

    def check_consistency(self, obj):
        is_consistent, message = obj.verify_quantities()
        if is_consistent:
            return "✓"
        return "❌"
    check_consistency.short_description = "Cohérence"

# Admin pour les instances de clés


@admin.register(KeyInstance)
class KeyInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'key_type', 'is_available',
                    'location', 'condition', 'get_assigned_to')
    list_filter = ('is_available', 'location', 'condition', 'key_type')
    search_fields = ('key_type__name', 'key_type__number', 'serial_number')
    inlines = [KeyAssignmentInstanceInline]

    def get_assigned_to(self, obj):
        """Affiche l'utilisateur à qui cette instance est attribuée."""
        try:
            if hasattr(obj, 'assignment') and obj.assignment.is_active:
                return f"{obj.assignment.user.firstname} {obj.assignment.user.name}"
        except:
            pass
        return "Non assignée"
    get_assigned_to.short_description = 'Attribuée à'

# Admin pour les équipes


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members_count')
    search_fields = ('name',)

    def get_members_count(self, obj):
        """Affiche le nombre d'utilisateurs dans cette équipe."""
        return obj.members.count()
    get_members_count.short_description = 'Nombre de membres'

# Admin pour les attributions de clés


@admin.register(KeyAssignment)
class KeyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('key_instance', 'user', 'assigned_date',
                    'return_date', 'is_active', 'comments')
    list_filter = ('is_active', 'assigned_date', 'return_date')
    search_fields = ('key_instance__key_type__name', 'key_instance__key_type__number',
                     'user__firstname', 'user__name', 'comments')
    date_hierarchy = 'assigned_date'
    list_editable = ('is_active',)
    raw_id_fields = ('key_instance', 'user')

# Admin pour les propriétaires (utilisateurs de l'application)


@admin.register(Owner)
class CustomOwnerAdmin(BaseUserAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Owner.
    Personnalise l'affichage, les filtres et les formulaires dans l'admin Django.
    """
    # Colonnes affichées dans la liste des utilisateurs
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'role', 'is_active')
    # Filtres disponibles dans la barre latérale
    list_filter = ('role', 'is_active', 'date_joined')
    # Organisation des champs dans la page de détail
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {
         'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
         'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Champs pour le formulaire d'ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_active'),
        }),
    )
    # Champs de recherche
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Ordre de tri par défaut
    ordering = ('last_name', 'first_name')

# IMPORTANT: Supprimez ces lignes qui causent des enregistrements en double
# admin.site.register(User, UserAdmin)
# admin.site.register(KeyType, KeyTypeAdmin)
# admin.site.register(KeyInstance, KeyInstanceAdmin)
# admin.site.register(Team, TeamAdmin)
# admin.site.register(KeyAssignment, KeyAssignmentAdmin)
# admin.site.register(Owner, OwnerAdmin)
