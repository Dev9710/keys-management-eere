"""
URL configuration for merchex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from listings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('about-us/', views.about),  # ajoutez cette ligne
    path('home/', views.home, name='home'),
    path('contact/', views.contact),
    path('users/', views.user_list, name='user_list'),
    path('teams/', views.team_list, name='team_list'),
    path('user_team/', views.user_team, name='user_team'),
    path('user_update/', views.user_update, name='user_update'),

    path('team_update/', views.team_update, name='team_update'),
    path('user_create/', views.user_create, name='user_create'),
    path('team_create/', views.team_create, name='team_create'),
    path('users/delete/<int:user_id>/', views.user_delete, name="user_delete"),
    path('user_delete/<int:user_id>/', views.user_delete, name="user_delete"),
    path('teams/delete/<int:team_id>/', views.team_delete, name="team_delete"),
    path('attr/', views.user_keys_view, name='user_keys'),
    path('get-assigned-keys/<int:user_id>/',
         views.get_assigned_keys, name='get_assigned_keys'),  # ok
    path('get-modal-assigned-keys/<int:user_id>/', views.get_modal_assigned_keys,
         name='get_modal_assigned_keys'),  # affiche les clés assigné ok
    path('keys/list/', views.key_list, name='key_list'),

    # Vue pour ajouter une clé
    path('keys/add/', views.key_create, name='key_create'),
    path('keys/update/', views.key_update,
         name='key_update'),  # URL for updating a key
    path('get_users_by_team/<int:team_id>/',
         views.get_users_by_team, name='get_users_by_team'),
    path('get_keys_by_user/<int:user_id>/',
         views.get_keys_by_user, name='get_keys_by_user'),
    path('key_delete/<int:key_id>/', views.key_delete, name='key_delete'),
    path('keys/bulk-delete/', views.bulk_key_delete, name='bulk_key_delete'),
    path('get-users-by-team/<int:team_id>/',
         views.get_users_by_team, name='get_users_by_team'),  # ok
    path('assign-keys/', views.assign_keys, name='assign_keys'),  # ok
    path('remove-all-keys/<int:user_id>/',
         views.remove_all_keys, name='remove_all_keys'),  # ok


    # URLs d'authentification de base
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Pages de tableau de bord par rôle
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('editor-dashboard/', views.editor_dashboard, name='editor_dashboard'),

    # Gestion des utilisateurs (admin uniquement)
    path('owner_management/', views.owner_management, name='owner_management'),
    path('add-owner/', views.add_owner, name='add_owner'),
    path('edit-owner/<int:user_id>/', views.update_owner, name='edit_owner'),
    path('delete-owner/<int:user_id>/', views.delete_owner, name='delete_owner'),

    # Page d'accès refusé
    path('access-denied/', views.access_denied, name='access_denied'),

    path('register/success/', views.register_success_view, name='register_success'),
]
