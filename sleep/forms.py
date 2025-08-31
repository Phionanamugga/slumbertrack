from django import forms
from .models import SleepSession, SleepGoal
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SleepSessionForm(forms.ModelForm):
    class Meta:
        model = SleepSession
        fields = ["start", "end", "quality", "latency_minutes", "awakenings", "tags", "notes"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

class SleepGoalForm(forms.ModelForm):
    class Meta:
        model = SleepGoal
        fields = ["target_hours", "target_bedtime", "target_waketime"]
        widgets = {
            "target_bedtime": forms.TimeInput(attrs={"type": "time"}),
            "target_waketime": forms.TimeInput(attrs={"type": "time"}),
        }

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
