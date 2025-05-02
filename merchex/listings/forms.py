# listings/forms.py
from django import forms
from .models import KeyType, KeyInstance, User, Team, Owner
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError


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


class OwnerCreationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé basé sur UserCreationForm.
    Ajoute les champs email, first_name et last_name comme obligatoires.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
        help_text="Votre adresse email sera utilisée pour les communications."
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )

    class Meta:
        model = Owner
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mise à jour des widgets pour les champs hérités
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})

    def clean_email(self):
        """Valide que l'email n'est pas déjà utilisé"""
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier si l'email existe déjà
            if Owner.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Cette adresse email est déjà utilisée.")
        return email

    def clean_username(self):
        """Valide que le nom d'utilisateur n'est pas déjà pris"""
        username = self.cleaned_data.get('username')
        if username:
            # Vérifier si le nom d'utilisateur existe déjà
            if Owner.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    "Ce nom d'utilisateur est déjà pris.")
        return username

    def save(self, commit=True):
        """Sauvegarde l'utilisateur avec les champs personnalisés"""
        owner = super().save(commit=False)
        owner.email = self.cleaned_data['email']
        owner.first_name = self.cleaned_data['first_name']
        owner.last_name = self.cleaned_data['last_name']
        # Le username est déjà sauvegardé par UserCreationForm, pas besoin de le réassigner
        owner.role = 'visitor'  # Par défaut, les nouveaux utilisateurs sont des visiteurs
        if commit:
            owner.save()
        return owner


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire d'authentification personnalisé avec des styles Bootstrap.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember_me'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['password'].label = "Mot de passe"


class OwnerUpdateForm(forms.ModelForm):
    """
    Formulaire pour la mise à jour du profil utilisateur.
    """
    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_last_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'})
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Formulaire de changement de mot de passe personnalisé avec des styles Bootstrap.
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Ancien mot de passe', 'id': 'id_old_password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe', 'id': 'id_new_password1'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirmer le nouveau mot de passe', 'id': 'id_new_password2'})
    )
