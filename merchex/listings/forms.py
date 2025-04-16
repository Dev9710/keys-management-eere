# listings/forms.py
from django import forms
from .models import Key, User, Team


class KeyForm(forms.ModelForm):
    class Meta:
        model = Key
        fields = [
            'number',
            'name',
            'place',
            'initial_key_number',
            'in_cabinet',
            'in_safe',
            'comments'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User  # Point to the correct model
        fields = [
            'firstname',
            'name',
            'team',
            'comment',
        ]
        widgets = {
            'team': forms.Select(attrs={'class': 'team-dropdown'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract user instance from kwargs
        user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if user_instance:
            # Filter keys by the user's assigned keys
            self.fields['keys'].queryset = Key.objects.filter(
                keys=user_instance)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team  # Point to the correct model
        fields = [
            'name',
        ]
        widgets = {
        }
