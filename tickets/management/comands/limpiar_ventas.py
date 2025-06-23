from django.core.management.base import BaseCommand
from django.db import transaction
from tickets.models import Venta, Boleto

class Command(BaseCommand):
    help = 'Elimina todos los registros de Venta y DetalleVenta, y resetea los contadores de boletos vendidos.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Este comando eliminará permanentemente todos los datos de ventas.'))
        confirmacion = input('¿Estás seguro de que quieres continuar? (s/n): ')

        if confirmacion.lower() != 's':
            self.stdout.write(self.style.ERROR('Operación cancelada.'))
            return

        try:
            with transaction.atomic():
                # Borrar todas las ventas y sus detalles en cascada
                num_ventas, _ = Venta.objects.all().delete()
                
                # Resetear contadores de boletos vendidos
                num_boletos = Boleto.objects.update(cantidad_vendida=0)

            self.stdout.write(self.style.SUCCESS(f'-------------------------------------------------'))
            self.stdout.write(self.style.SUCCESS(f'Limpieza completada con éxito:'))
            self.stdout.write(self.style.SUCCESS(f'- Se eliminaron {num_ventas} ventas.'))
            self.stdout.write(self.style.SUCCESS(f'- Se reiniciaron los contadores de {num_boletos} boletos.'))
            self.stdout.write(self.style.SUCCESS(f'-------------------------------------------------'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error durante la limpieza: {e}'))