from django import forms
from .models import Team, Player


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['city', 'mascot']


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'teams']
        widgets = {'teams': forms.CheckboxSelectMultiple}
        help_texts = {'teams': 'Leave every box clear for a player without a team.'}
