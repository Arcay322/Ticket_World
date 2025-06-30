# tickets/forms.py
from django import forms
from django.utils import timezone
from .models import Evento, Boleto, Opinion, Categoria
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        # ==========================================================
        # === CAMBIO PRINCIPAL: Actualizamos la lista de campos ===
        # ==========================================================
        fields = [
            'nombre', 
            'descripcion', 
            'fecha', 
            'categoria', 
            'imagen_portada',
            # --- Bloque de ubicación completo ---
            'lugar_nombre',
            'direccion',
            'ciudad',
            'pais',
            'latitud',
            'longitud',
            'mapa_enlace_embed', # <-- ¡Añade este campo!
        ]
        # ==========================================================
        # === FIN DEL CAMBIO ===
        # ==========================================================

        # Actualizamos las etiquetas y widgets para los nuevos campos
        labels = {
            'nombre': 'Nombre del Evento',
            'descripcion': 'Descripción Detallada',
            'fecha': 'Fecha y Hora del Evento',
            'categoria': 'Categoría',
            'imagen_portada': 'Imagen de Portada (Opcional)',
            'lugar_nombre': 'Nombre del Lugar o Recinto',
            'direccion': 'Dirección Completa del Evento',
            'ciudad': 'Ciudad',
            'pais': 'País',
            'latitud': 'Latitud (para mapas)',
            'longitud': 'Longitud (para mapas)',
            'mapa_enlace_embed': 'Enlace del Mapa Incrustado (se genera automáticamente)', # <-- Añade esta etiqueta
        }
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe los detalles de tu evento...'}),
            'imagen_portada': forms.ClearableFileInput(),
            'lugar_nombre': forms.TextInput(attrs={'placeholder': 'Ej: Estadio Nacional'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej: Av. José Díaz s/n, Cercado de Lima'}),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ej: Lima'}),
            'pais': forms.TextInput(attrs={'placeholder': 'Ej: Perú'}),
            'latitud': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Ej: -12.067821', 'readonly': 'readonly'}), # <-- Hazlo readonly
            'longitud': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Ej: -77.033478', 'readonly': 'readonly'}), # <-- Hazlo readonly
            'mapa_enlace_embed': forms.URLInput(attrs={'readonly': 'readonly'}), # <-- Nuevo widget, también readonly
        }

    # Tu lógica de inicialización y validación se mantiene igual
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.fecha:
            # Aseguramos que el formato de fecha sea compatible con el widget
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')
        
        # Hacemos que la latitud, longitud y mapa_enlace_embed no sean obligatorias
        # y que el usuario no las vea directamente ni las edite.
        self.fields['latitud'].required = False
        self.fields['longitud'].required = False
        self.fields['mapa_enlace_embed'].required = False # <-- ¡Hazlo no requerido!

        # Esto asegura que los campos no se muestren en el formulario renderizado por {{ form.as_p }}
        # y solo se rellenarán con JavaScript.
        self.fields['latitud'].widget = forms.HiddenInput()
        self.fields['longitud'].widget = forms.HiddenInput()
        self.fields['mapa_enlace_embed'].widget = forms.HiddenInput()


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

# ================================================================
# === El resto de tus formularios no necesitan modificaciones ===
# ================================================================
class BoletoForm(forms.ModelForm):
    anadir_quitar_stock = forms.IntegerField(
        label="Añadir/Quitar Boletos",
        required=False,
        help_text="Usa un número positivo para añadir (ej: 50) o negativo para quitar (ej: -10)."
    )

    class Meta:
        model = Boleto
        fields = ['tipo', 'nombre_boleto', 'precio', 'cantidad_total']
        extra_kwargs = { 'cantidad_total': {'required': False} }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or not self.instance.pk:
            self.fields.pop('anadir_quitar_stock', None)
        else:
            self.fields.pop('cantidad_total', None)

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            anadir_quitar = cleaned_data.get('anadir_quitar_stock')
            if anadir_quitar:
                nueva_cantidad_total = self.instance.cantidad_total + anadir_quitar
                if nueva_cantidad_total < self.instance.cantidad_vendida:
                    raise forms.ValidationError(f"No puedes reducir el stock a {nueva_cantidad_total}. Ya se han vendido {self.instance.cantidad_vendida} boletos.")
        else:
            if not cleaned_data.get('DELETE'):
                if self.has_changed() and not cleaned_data.get('cantidad_total'):
                    raise forms.ValidationError("Debes especificar la 'Cantidad Total Disponible' para los boletos nuevos.")
        return cleaned_data

class BaseBoletoFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if form.prefix and form.data.get(f'{form.prefix}-tipo') == 'conadis':
                form.fields['precio'].required = False

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

BoletoFormSetCreate = inlineformset_factory(
    Evento, Boleto, form=BoletoForm, formset=BaseBoletoFormSet,
    extra=1, min_num=1, can_delete=True, validate_min=True
)

BoletoFormSetEdit = inlineformset_factory(
    Evento, Boleto, form=BoletoForm, formset=BaseBoletoFormSet,
    extra=0, min_num=1, can_delete=True, validate_min=True
)

class StarRatingWidget(forms.RadioSelect):
    template_name = 'tickets/widgets/star_rating_widget.html'

class OpinionForm(forms.ModelForm):
    CALIFICACION_CHOICES = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
    ]
    
    calificacion = forms.ChoiceField(
        label="Tu Calificación (1-5 estrellas)",
        choices=CALIFICACION_CHOICES,
        widget=StarRatingWidget()
    )

    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Comparte tu experiencia...'}),
        required=False,
        label="Tu Comentario"
    )

    class Meta:
        model = Opinion
        fields = ['calificacion', 'comentario']