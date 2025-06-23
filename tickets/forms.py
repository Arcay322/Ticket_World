# tickets/forms.py
from django import forms
from django.utils import timezone
from .models import Evento, Boleto, Opinion, Categoria
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')

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
    anadir_quitar_stock = forms.IntegerField(
        label="Añadir/Quitar Boletos",
        required=False,
        help_text="Usa un número positivo para añadir (ej: 50) o negativo para quitar (ej: -10)."
    )

    class Meta:
        model = Boleto
        fields = ['tipo', 'nombre_boleto', 'precio', 'cantidad_total']
        # Hacemos que cantidad_total no sea requerido a nivel de formulario,
        # ya que nuestra lógica clean se encarga de validarlo.
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
            # Solo validamos cantidad_total para formularios nuevos que no están marcados para borrar
            if not cleaned_data.get('DELETE'):
                if self.has_changed() and not cleaned_data.get('cantidad_total'):
                    raise forms.ValidationError("Debes especificar la 'Cantidad Total Disponible' para los boletos nuevos.")
        return cleaned_data


class BaseBoletoFormSet(BaseInlineFormSet):
    # --- INICIO DE LA LÓGICA AÑADIDA ---
    # Este __init__ se ejecuta ANTES de la validación.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            # Comprobamos si el tipo de boleto en los datos enviados es 'conadis'
            # La clave del campo en form.data tiene un prefijo, ej: 'boletos-0-tipo'
            if form.prefix and form.data.get(f'{form.prefix}-tipo') == 'conadis':
                # Si es CONADIS, hacemos que el campo de precio NO sea obligatorio.
                # Esto permite que formset.is_valid() devuelva True.
                form.fields['precio'].required = False
    # --- FIN DE LA LÓGICA AÑADIDA ---

    # Tu lógica existente se mantiene intacta, lo cual es correcto.
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        valid_forms_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                valid_forms_count += 1
        # Usamos self.min_num que definimos en el factory.
        if valid_forms_count < self.min_num:
            raise forms.ValidationError(f"Debes proporcionar al menos {self.min_num} tipo de boleto.")


# Estas definiciones ya usan tu BaseBoletoFormSet, así que heredarán la nueva lógica.
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