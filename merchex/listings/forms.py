# listings/forms.py
from django import forms
from .models import Key,User,Team

class KeyForm(forms.ModelForm):
    class Meta:
        model = Key
        fields = [
            'number',
            'name',
            'place',
            'initial_key_number',
            'key_used',
            'key_available',
            'in_cabinet',
            'in_safe',
            'comments'
        ]
        widgets = {
            'in_cabinet': forms.CheckboxInput(),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

class UserForm(forms.ModelForm):
    # Change 'owner' to be a list of keys
    keys = forms.ModelMultipleChoiceField(
        queryset=Key.objects.none(),  # Start with an empty queryset
        widget=forms.SelectMultiple(attrs={'size': '5'}),  # Dropdown with multiple selections
        required=False  # Optional: Set to True if at least one key must be selected
    )

    class Meta:
        model = User  # Point to the correct model
        fields = [
            'firstname',
            'name',
            'team',
            'keys',  # Use 'keys' instead of 'owner'
        ]
        widgets = {
            'firstname': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
            'team': forms.Select(attrs={'class': 'team-dropdown'}),
        }

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)  # Extract user instance from kwargs
        super().__init__(*args, **kwargs)
        if user_instance:
            # Filter keys by the user's assigned keys
            self.fields['keys'].queryset = Key.objects.filter(keys=user_instance)