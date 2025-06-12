# tickets/forms.py

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Evento, Categoria, Boleto
from django.utils import timezone

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'fecha', 'categoria', 'lugar', 'direccion', 'imagen_portada']
        labels = {
            'nombre': 'Nombre del Evento',
            'descripcion': 'Descripción Detallada',
            'fecha': 'Fecha y Hora del Evento',
            'categoria': 'Categoría',
            'lugar': 'Lugar del Evento',
            'direccion': 'Dirección Completa del Evento',
            'imagen_portada': 'Imagen de Portada (Opcional)',
        }
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 5}),
            'imagen_portada': forms.ClearableFileInput(),
        }

    # === ESTE MÉTODO __init__ ES LA SOLUCIÓN ===
    # Se asegura de que la fecha se muestre correctamente al editar.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el formulario está editando un evento que ya existe...
        if self.instance and self.instance.pk and self.instance.fecha:
            # ...formateamos la fecha al formato que el widget HTML necesita ('YYYY-MM-DDTHH:MM').
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')
        
        # Mantenemos la lógica para ordenar las categorías
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')

    # --- Tus validaciones (están perfectas, se quedan igual) ---
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
    # Definimos ambos campos en la clase
    anadir_quitar_stock = forms.IntegerField(
        label="Añadir/Quitar Boletos",
        required=False,
        help_text="Usa un número positivo para añadir (ej: 50) o negativo para quitar (ej: -10)."
    )

    class Meta:
        model = Boleto
        fields = ['tipo', 'nombre_boleto', 'precio', 'cantidad_total']
        extra_kwargs = { 'cantidad_total': {'required': False} }
        # ... (Tus otros labels y widgets se quedan igual)

    # === MÉTODO __init__ AÑADIDO PARA LA LÓGICA INTELIGENTE ===
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # self.instance es el objeto Boleto que se está editando.
        # Si no existe (es decir, es un formulario para un boleto nuevo)...
        if not self.instance or not self.instance.pk:
            # ...eliminamos el campo 'anadir_quitar_stock' que no tiene sentido aquí.
            self.fields.pop('anadir_quitar_stock')
        else:
            # Si SÍ estamos editando un boleto que ya existe...
            # ...eliminamos el campo 'cantidad_total' que es confuso.
            self.fields.pop('cantidad_total')

    def clean(self):
        # ... (Tu método clean se queda exactamente igual, está perfecto)
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            anadir_quitar = cleaned_data.get('anadir_quitar_stock')
            if anadir_quitar:
                nueva_cantidad_total = self.instance.cantidad_total + anadir_quitar
                if nueva_cantidad_total < self.instance.cantidad_vendida:
                    raise forms.ValidationError(f"No puedes reducir el stock a {nueva_cantidad_total}. Ya se han vendido {self.instance.cantidad_vendida} boletos.")
        else:
            if self.has_changed() and not cleaned_data.get('cantidad_total'):
                 raise forms.ValidationError("Debes especificar la 'Cantidad Total Disponible' para los boletos nuevos.")
        return cleaned_data


class BaseBoletoFormSet(BaseInlineFormSet):
    # Esta lógica es la que nos permite eliminar el último boleto sin errores.
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        valid_forms_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                valid_forms_count += 1
        if valid_forms_count < self.min_num:
            raise forms.ValidationError(f"Debes proporcionar al menos {self.min_num} tipo de boleto.")


# === DEFINIMOS NUESTRAS DOS "RECETAS" DE FORMSET ===

# Receta para CREAR eventos: Necesita al menos 1 boleto y muestra 1 formulario extra.
BoletoFormSetCreate = inlineformset_factory(
    Evento, Boleto, form=BoletoForm, formset=BaseBoletoFormSet,
    extra=1, min_num=1, can_delete=True, validate_min=True
)

# Receta para EDITAR eventos: NO muestra formularios extra.
BoletoFormSetEdit = inlineformset_factory(
    Evento, Boleto, form=BoletoForm, formset=BaseBoletoFormSet,
    extra=0, min_num=1, can_delete=True, validate_min=True # Mantenemos el mínimo de 1 boleto por evento
)