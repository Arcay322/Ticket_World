# reports/urls.py (CONTENIDO COMPLETO)

from django.urls import path
from . import views # Asegúrate de que importa views de la app reports

app_name = 'reports' # Nombre de la app para URLs

urlpatterns = [
    # La raíz de la app 'reports' en el admin apuntará a tu dashboard.
    # Esta URL será accesible como /admin/reports/
    path('', views.reports_dashboard_view, name='index'), # 'index' es el nombre canónico para la raíz de una app
    # Puedes añadir más URLs de reportes específicos aquí en el futuro
    # path('ventas/', views.sales_report_detail, name='sales_report'),
]