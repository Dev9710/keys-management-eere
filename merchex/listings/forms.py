# listings/forms.py
from django import forms
from .models import KeyType, KeyInstance, User, Team


class KeyForm(forms.ModelForm):
    class Meta:
        model = KeyType
        fields = [
            'number',
            'name',
            'place',
            'total_quantity',
            'in_cabinet',
            'in_safe',
            'comments'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    # Ajouter des indications pour les champs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_quantity'].help_text = "Nombre total d'exemplaires de cette clé"
        self.fields['in_cabinet'].help_text = "Nombre d'exemplaires stockés dans l'armoire"
        self.fields['in_safe'].help_text = "Nombre d'exemplaires stockés dans le coffre"


class KeyInstanceForm(forms.ModelForm):
    """Formulaire pour gérer les instances individuelles de clés"""
    class Meta:
        model = KeyInstance
        fields = [
            'key_type',
            'serial_number',
            'condition',
            'location',
            'comments'
        ]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'firstname',
            'name',
            'team',
            'comment',
        ]
        widgets = {
            'team': forms.Select(attrs={'class': 'team-dropdown'}),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name',
        ]
