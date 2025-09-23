from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

tailwind_input_classes = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos las clases de Tailwind a cada campo del formulario
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = tailwind_input_classes

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos lo mismo para el formulario de login
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = tailwind_input_classes