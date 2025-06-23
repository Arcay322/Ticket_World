# reports/admin.py

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import ReportDashboard # Importa el modelo dummy

@admin.register(ReportDashboard)
class ReportDashboardAdmin(admin.ModelAdmin):
    list_display = ('name',)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request): return False
    def has_view_permission(self, request, obj=None): return True

    # --- ¡CLAVE AQUÍ! CORRECCIÓN DEL NOMBRE EN reverse() ---
    def changelist_view(self, request, extra_context=None):
        # Redirige a la URL de tu dashboard real, que ahora se llama 'reports:index'
        return redirect(reverse('reports:index')) # <-- ¡CORREGIDO A 'reports:index'!