from django.contrib import admin
from .models import Categoria, Evento, Boleto, MetodoPago, Venta, DetalleVenta, Opinion

admin.site.register(Categoria)
admin.site.register(Evento)
admin.site.register(Boleto)
admin.site.register(MetodoPago)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Opinion)