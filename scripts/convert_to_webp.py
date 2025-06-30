import os
from PIL import Image

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'media', 'eventos')

# Extensiones de imagen soportadas
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

def convert_to_webp(image_path):
    webp_path = os.path.splitext(image_path)[0] + '.webp'
    if os.path.exists(webp_path):
        print(f"Ya existe: {webp_path}")
        return
    try:
        with Image.open(image_path) as img:
            img.save(webp_path, 'webp', quality=85)
        print(f"Convertido: {image_path} -> {webp_path}")
    except Exception as e:
        print(f"Error al convertir {image_path}: {e}")

def convert_all_images():
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                image_path = os.path.join(root, file)
                convert_to_webp(image_path)

if __name__ == "__main__":
    convert_all_images()
    print("Conversión a WebP finalizada.")
