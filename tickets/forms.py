# tickets/forms.py

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet # <-- AÑADE BaseInlineFormSet
from .models import Evento, Categoria, Boleto
from django.utils import timezone

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'fecha', 'categoria', 'lugar', 'direccion', 'imagen_portada']
        labels = { 'nombre': 'Nombre del Evento', 'descripcion': 'Descripción Detallada', 'fecha': 'Fecha y Hora del Evento', 'categoria': 'Categoría', 'lugar': 'Lugar del Evento', 'direccion': 'Dirección Completa del Evento', 'imagen_portada': 'Imagen de Portada (Opcional)', }
        widgets = { 'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 'descripcion': forms.Textarea(attrs={'rows': 5}), }
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("La fecha del evento no puede ser en el pasado.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        fecha = cleaned_data.get("fecha")
        if nombre and fecha:
            if Evento.objects.filter(nombre=nombre, fecha=fecha).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un evento con este mismo nombre programado para esa fecha y hora.")
        return cleaned_data

class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = ['tipo', 'nombre_boleto', 'precio', 'cantidad_total']
        labels = { 'tipo': 'Tipo de Boleto', 'nombre_boleto': 'Nombre Específico (Opcional)', 'precio': 'Precio del Boleto', 'cantidad_total': 'Cantidad Total Disponible', }
        widgets = { 'tipo': forms.Select(), 'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}), 'cantidad_total': forms.NumberInput(attrs={'min': '1'}), }

# === CLASE PERSONALIZADA PARA LA LÓGICA DE ELIMINACIÓN ===
class BaseBoletoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Contamos cuántos formularios no están marcados para eliminación
        active_forms = 0
        for form in self.forms:
            # .is_valid() es importante para no contar formularios con errores
            # y not form.cleaned_data.get('DELETE', False) para ignorar los marcados
            if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                active_forms += 1
        
        # Si el conteo de formularios activos es menor que el mínimo requerido, lanzamos el error
        if active_forms < self.min_num:
            raise forms.ValidationError(f"Debes proporcionar al menos {self.min_num} tipo de boleto.")

# === MODIFICAMOS EL FORMSET PARA QUE USE NUESTRA CLASE PERSONALIZADA ===
BoletoFormSet = inlineformset_factory(
    Evento, 
    Boleto, 
    form=BoletoForm,
    formset=BaseBoletoFormSet, # <-- AÑADIMOS ESTA LÍNEA
    extra=1, 
    can_delete=True,
    min_num=1, 
    validate_min=True, 
)