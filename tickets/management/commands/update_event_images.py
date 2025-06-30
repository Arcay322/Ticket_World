# tickets/management/commands/update_event_images.py

import os
import random
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from tickets.models import Evento, Categoria
from django.core.files import File # ¡Importa la clase File!

class Command(BaseCommand):
    help = 'Actualiza las imágenes de portada de los eventos automáticamente, como una subida manual.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando script para actualizar las imágenes de los eventos automáticamente..."))
        self.stdout.write(self.style.WARNING("Este script leerá las imágenes desde 'static/img/' y las copiará a tu carpeta 'media/eventos/'."))

        # Define el directorio base donde se encuentran tus imágenes estáticas.
        # Asumiendo que tu settings.STATICFILES_DIRS incluye BASE_DIR / 'static'
        # y que las imágenes están en 'static/img/'
        STATIC_IMG_FULL_DIR_PATH = os.path.join(settings.BASE_DIR, 'static', 'img')

        # Define las imágenes para cada categoría con sus NOMBRES DE ARCHIVO.
        # El script las buscará en STATIC_IMG_FULL_DIR_PATH
        DEPORTES_IMAGE_FILENAME = 'categoria_deportes.png'

        CONCIERTO_IMAGE_FILENAMES = [
            'Concierto_Mon_Laferte.png',
            'Concierto_Mora.png',
            'Concierto_Quevedo.png',
            'Concierto_Trueno.png',
            'Concierto_Chayanne.png',
            'Concierto_Duki.png',
            'Concierto_Amen.png',
            'Concierto_Paulo_Londra.png',
        ]

        updated_count = 0
        skipped_count = 0

        # Obtener las categorías por nombre para evitar múltiples consultas dentro del bucle
        deportes_categoria = None
        try:
            deportes_categoria = Categoria.objects.get(nombre__iexact='Deportes')
            self.stdout.write(self.style.SUCCESS(f"Categoría 'Deportes' encontrada (ID: {deportes_categoria.id})."))
        except Categoria.DoesNotExist:
            self.stdout.write(self.style.WARNING("ADVERTENCIA: Categoría 'Deportes' no encontrada. Los eventos de deportes no se actualizarán."))

        concierto_categoria = None
        try:
            # ¡¡¡CORRECCIÓN CLAVE AQUÍ!!! CAMBIADO 'Conciertos' a 'Concierto'
            concierto_categoria = Categoria.objects.get(nombre__iexact='Concierto') 
            self.stdout.write(self.style.SUCCESS(f"Categoría 'Concierto' encontrada (ID: {concierto_categoria.id})."))
        except Categoria.DoesNotExist:
            self.stdout.write(self.style.WARNING("ADVERTENCIA: Categoría 'Concierto' no encontrada. Los eventos de conciertos no se actualizarán."))


        for evento in Evento.objects.all():
            old_image_path = evento.imagen_portada.name if evento.imagen_portada else 'N/A'
            
            source_image_filename = None # Nombre del archivo a buscar en static/img/

            if deportes_categoria and evento.categoria == deportes_categoria:
                source_image_filename = DEPORTES_IMAGE_FILENAME
                self.stdout.write(f"Evento '{evento.nombre}' (ID: {evento.id}) es de Deportes. Asignando imagen: {source_image_filename}")
            elif concierto_categoria and evento.categoria == concierto_categoria:
                # Asegúrate de que el mensaje de log también refleje el nombre correcto de la categoría
                self.stdout.write(f"Evento '{evento.nombre}' (ID: {evento.id}) es de Concierto. Asignando aleatoriamente imagen.")
                source_image_filename = random.choice(CONCIERTO_IMAGE_FILENAMES)
            else:
                self.stdout.write(f"Evento '{evento.nombre}' (ID: {evento.id}) no coincide con categorías predefinidas o categoría no encontrada. Se mantiene la imagen actual: {old_image_path}")
                skipped_count += 1
                continue

            if source_image_filename:
                full_source_path = os.path.join(STATIC_IMG_FULL_DIR_PATH, source_image_filename)

                if not os.path.exists(full_source_path):
                    self.stdout.write(self.style.ERROR(f"ERROR: El archivo de imagen '{full_source_path}' no se encontró. Saltando evento '{evento.nombre}'."))
                    skipped_count += 1
                    continue

                try:
                    with open(full_source_path, 'rb') as f:
                        evento.imagen_portada.save(source_image_filename, File(f), save=False)

                    evento.save(update_fields=['imagen_portada'])
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  > Imagen de '{evento.nombre}' actualizada de '{old_image_path}' a '{evento.imagen_portada.name}' (copiada a MEDIA_ROOT)."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"ERROR procesando imagen para '{evento.nombre}' (ID: {evento.id}): {e}. Saltando evento."))
                    skipped_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS("\n--- Resumen de la Actualización ---"))
        self.stdout.write(self.style.SUCCESS(f"Eventos actualizados: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Eventos omitidos (sin categoría, categoría no coincidente, o archivo no encontrado/error): {skipped_count}"))
        self.stdout.write(self.style.SUCCESS("¡Script de actualización de imágenes completado!"))