from django import forms
from django.contrib.auth.models import User
from .models import CustomUser, CustomerProfile, RailwayStaffProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class CustomUserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password")
