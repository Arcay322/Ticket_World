# tickets/forms.py
from django import forms
from django.forms import inlineformset_factory 
from .models import Evento, Categoria, Boleto # Importamos los modelos

class EventoForm(forms.ModelForm):
    # Campos del formulario para crear un Evento
    class Meta:
        model = Evento
        # Campos que el proveedor debe rellenar
        # 'creado_por', 'aprobado', 'esta_activo', 'esta_agotado', 'creado_en', 'actualizado_en'
        # son campos de backend y no deben ser editables por el usuario en el formulario.
        fields = ['nombre', 'descripcion', 'fecha', 'categoria', 'lugar', 'direccion', 'imagen_portada']
        
        # Etiquetas personalizadas para los campos
        labels = {
            'nombre': 'Nombre del Evento',
            'descripcion': 'Descripción Detallada',
            'fecha': 'Fecha y Hora del Evento',
            'categoria': 'Categoría',
            'lugar': 'Lugar del Evento',
            'direccion': 'Dirección Completa del Evento',
            'imagen_portada': 'Imagen de Portada (Opcional)',
        }
        
        # Widgets para mejorar la experiencia de usuario
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: Personalizar el queryset de categorías si fuera necesario
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')


# Formulario para un Boleto individual
class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        # No incluimos 'evento' aquí, ya que el formset lo manejará automáticamente
        fields = ['tipo', 'nombre_boleto', 'precio', 'cantidad_total']
        labels = {
            'tipo': 'Tipo de Boleto',
            'nombre_boleto': 'Nombre Específico (Opcional)',
            'precio': 'Precio del Boleto',
            'cantidad_total': 'Cantidad Total Disponible',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre_boleto': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'cantidad_total': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

# Creamos un formset para el modelo Boleto, relacionado con Evento
# extra=1: Muestra 1 formulario de boleto vacío por defecto
# can_delete=True: Permite al usuario eliminar boletos existentes (útil para edición)
# max_num: Opcional, limita el número máximo de boletos que se pueden añadir
# min_num=1: Asegura que al menos un tipo de boleto sea creado con el evento.
BoletoFormSet = inlineformset_factory(
    Evento, 
    Boleto, 
    form=BoletoForm, 
    extra=1, 
    can_delete=True,
    min_num=1, 
    validate_min=True, 
)

