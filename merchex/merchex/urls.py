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
    path('listing/', views.listing),
    path('contact/', views.contact),
    path('users/', views.user_list, name='user_list'),
    path('user_team/', views.user_team, name='user_team'),
    path('user_update/', views.user_update, name='user_update'),
    path('user_create/', views.user_create, name='user_create'),
    path('users/delete/<int:user_id>/', views.user_delete, name="user_delete"),
    path('attr/', views.user_keys_view, name='user_keys'),
    path('get-assigned-keys/<int:user_id>/',
         views.get_assigned_keys, name='get_assigned_keys'),
    path('get-modal-assigned-keys/<int:user_id>/', views.get_modal_assigned_keys,
         name='get_modal_assigned_keys'),  # affiche les clés assigné
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
         views.get_users_by_team, name='get_users_by_team'),
    path('assign-keys/', views.assign_keys, name='assign_keys'),
]
