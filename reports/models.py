# reports/models.py

from django.db import models

class ReportDashboard(models.Model): # <-- ¡Este es el modelo!
    # Este modelo no almacena datos reales.
    # Sirve como un marcador de posición para hacer que la app 'reports' sea visible en Django Admin.
    name = models.CharField(max_length=50, default="Dashboard de Reportes", editable=False)

    class Meta:
        verbose_name = "Dashboard de Reportes"
        verbose_name_plural = "Dashboard de Reportes"
        app_label = 'reports' 
        default_permissions = () 
        permissions = [("view_report_dashboard", "Can view report dashboard"),]

    def __str__(self):
        return self.name