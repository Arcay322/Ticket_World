# ticket_world/management/commands/test_notifications.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.utils import get_unread_admin_notifications_count
from django.test import RequestFactory
from tickets.models import AdminNotification

class Command(BaseCommand):
    help = 'Prueba la función get_unread_admin_notifications_count y crea una notificación de prueba.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- INICIANDO PRUEBA DE CONTEO EN CONSOLA (VIA COMANDO) ---'))

        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()

        if admin_user:
            factory = RequestFactory()
            req = factory.get('/admin/')
            req.user = admin_user

            initial_count = get_unread_admin_notifications_count(req)
            self.stdout.write(self.style.SUCCESS(f"SHELL TEST: Conteo inicial para {admin_user.username}: {initial_count}"))

            # Crea una notificación de prueba para ver si el conteo cambia
            try:
                AdminNotification.objects.create(
                    recipient=admin_user,
                    type='general',
                    message='Notificación de prueba desde el comando',
                    link='/admin/'
                )
                self.stdout.write(self.style.SUCCESS("SHELL TEST: Notificación de prueba creada."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERROR al crear notificación de prueba: {e}"))

            new_count = get_unread_admin_notifications_count(req)
            self.stdout.write(self.style.SUCCESS(f"SHELL TEST: Conteo después de crear notificación: {new_count}"))

            self.stdout.write(self.style.SUCCESS('--- FIN DE PRUEBA DE CONTEO EN CONSOLA (VIA COMANDO) ---\n'))

        else:
            self.stdout.write(self.style.WARNING("SHELL TEST: ¡ADVERTENCIA! No se encontró ningún superusuario. No se puede probar el conteo."))