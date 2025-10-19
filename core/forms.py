# core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Неверный логин или пароль. Пожалуйста, попробуйте снова."
        ),
        'inactive': ("Этот аккаунт неактивен."),
    }