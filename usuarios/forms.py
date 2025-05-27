from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from .models import SolicitudProveedor

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']  # Sin el campo 'rol'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario o Email")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class SolicitudProveedorForm(forms.ModelForm):
    class Meta:
        model = SolicitudProveedor
        fields = ['nombres', 'apellidos', 'email', 'telefono', 'nombre_empresa', 'descripcion']
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'nombre_empresa': 'Nombre de la Empresa',
            'descripcion': 'Descripción de los Servicios',
        }


    # Agregar validaciones si es necesario
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and len(telefono) < 9:
            raise forms.ValidationError("El teléfono debe tener al menos 9 dígitos.")
        return telefono