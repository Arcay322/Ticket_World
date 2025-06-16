from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario # Asumo que tu modelo de usuario personalizado se llama 'Usuario'
from .models import SolicitudProveedor
from django.contrib.auth import get_user_model  # Importa el modelo de usuario actual

# --- ¡AÑADE ESTA LÍNEA AQUÍ! ---
User = get_user_model()
# ---------------------------------

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
    
    
class UserProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    username = forms.CharField(max_length=150, required=True, label="Nombre de Usuario")

    class Meta:
        # Aquí se usa la variable User que acabamos de definir
        model = User 
        fields = ['username', 'email'] # Puedes añadir otros campos como 'first_name', 'last_name' si los tienes

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Asegúrate de que el email no esté ya en uso por otro usuario
        # Usa User.objects.filter porque User ya está definido globalmente en este archivo
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso por otra cuenta.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Usa User.objects.filter aquí también
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso por otra cuenta.")
        return username

class ReenviarActivacionForm(forms.Form):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu email'})
    )