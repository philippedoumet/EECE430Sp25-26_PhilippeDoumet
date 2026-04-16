from django import forms
from django.contrib.auth.models import User
from .models import (
    Player, Match, Training, Attendance,
    PlayerStatistic, Transfer, Expense, Season, Coach
)

BOOTSTRAP = 'form-control'
BOOTSTRAP_SELECT = 'form-select'
BOOTSTRAP_CHECK = 'form-check-input'


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': 'e.g. 2025-2026'}),
            'start_date': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ['user']
        widgets = {
            'name': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'date_joined': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'position': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'salary': forms.NumberInput(attrs={'class': BOOTSTRAP}),
            'contact_person': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'phone': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'jersey_number': forms.NumberInput(attrs={'class': BOOTSTRAP}),
            'birth_date': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'height_cm': forms.NumberInput(attrs={'class': BOOTSTRAP}),
            'is_active': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class PlayerAccountForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Choose a username'})
    )
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': BOOTSTRAP})
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': BOOTSTRAP})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        data = super().clean()
        if data.get('password') != data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return data


class CoachProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': BOOTSTRAP}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': BOOTSTRAP}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': BOOTSTRAP}))

    class Meta:
        model = Coach
        fields = ['phone', 'specialty']
        widgets = {
            'phone': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'specialty': forms.TextInput(attrs={'class': BOOTSTRAP}),
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['season', 'date', 'opponent', 'venue', 'match_type', 'sets_won', 'sets_lost', 'notes']
        widgets = {
            'season': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'date': forms.DateTimeInput(attrs={'class': BOOTSTRAP, 'type': 'datetime-local'}),
            'opponent': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'venue': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'match_type': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'sets_won': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'sets_lost': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'notes': forms.Textarea(attrs={'class': BOOTSTRAP, 'rows': 3}),
        }


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['season', 'date', 'location', 'description']
        widgets = {
            'season': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'date': forms.DateTimeInput(attrs={'class': BOOTSTRAP, 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'description': forms.Textarea(attrs={'class': BOOTSTRAP, 'rows': 3}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['player', 'status', 'reason']
        widgets = {
            'player': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'status': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'reason': forms.TextInput(attrs={'class': BOOTSTRAP}),
        }


class PlayerStatisticForm(forms.ModelForm):
    class Meta:
        model = PlayerStatistic
        fields = ['player', 'points', 'kills', 'aces', 'blocks', 'digs', 'errors', 'minutes_played', 'rating']
        widgets = {
            'player': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'points': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'kills': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'aces': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'blocks': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'digs': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'errors': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'minutes_played': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0}),
            'rating': forms.NumberInput(attrs={'class': BOOTSTRAP, 'min': 0, 'max': 10, 'step': 0.1}),
        }


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['player', 'transfer_type', 'from_club', 'to_club', 'fee', 'date', 'season', 'notes']
        widgets = {
            'player': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'transfer_type': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'from_club': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'to_club': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'fee': forms.NumberInput(attrs={'class': BOOTSTRAP}),
            'date': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'season': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'notes': forms.Textarea(attrs={'class': BOOTSTRAP, 'rows': 3}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description', 'season']
        widgets = {
            'category': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'amount': forms.NumberInput(attrs={'class': BOOTSTRAP}),
            'date': forms.DateInput(attrs={'class': BOOTSTRAP, 'type': 'date'}),
            'description': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'season': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
        }
