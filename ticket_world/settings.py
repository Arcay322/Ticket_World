# settings.py

"""
Django settings for ticket_world project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Cargar variables de entorno desde .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# La SECRET_KEY se leerá desde las variables de entorno. 
# Se mantiene un valor por defecto solo para desarrollo local si no está en .env.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-4o4waal&@#kcb0s&)@f00-e3&t#v7ic-cf)2n57%e95au1@nl+')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG se lee desde el entorno. Por defecto es False en producción.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS se lee desde el entorno.
# En Render, deberías poner 'tu-dominio.onrender.com'.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Añadir el hostname de Render a ALLOWED_HOSTS si está disponible
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    # --- JAZZMIN START ---
    'jazzmin',  # ¡MUY IMPORTANTE: DEBE IR ANTES DE django.contrib.admin!
    # --- JAZZMIN END ---

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'ticket_world', # Correctamente incluido

    # App de notificaciones (si la usas para otras cosas o si necesitas un admin para ellas)
    # 'notifications', # DESINSTALADO Y REMOVIDO AL USAR SISTEMA CUSTOM

    # Tus aplicaciones personalizadas
    'usuarios', # Tu app de usuarios
    'tickets',  # Tu app de tickets
    'reports', # Removido anteriormente
    
    'corsheaders',  # Nueva app para manejar CORS
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     # Reactivado para diagnóstico
]

ROOT_URLCONF = 'ticket_world.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates', # Ruta a tu carpeta de plantillas a nivel de proyecto
        ],
        'APP_DIRS': True, # Crucial para que Django busque plantillas dentro de los directorios 'templates' de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ticket_world.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        default=os.environ.get('DATABASE_URL')
    )
}

AUTH_USER_MODEL = 'usuarios.Usuario'
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = '/inicio/' # O 'usuarios:inicio' si tienes una URL con nombre para el inicio
LOGOUT_REDIRECT_URL = 'login' # O 'usuarios:login' o 'usuarios:despedida'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static', # Ruta a una carpeta 'static' en la raíz de tu proyecto
]
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directorio donde se recolectarán los estáticos en producción

# WhiteNoise: configuración para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CONFIGURACIÓN DE ARCHIVOS DE MEDIOS (MEDIA FILES) ---
if 'USE_GCS' in os.environ:
    # Configuración para Google Cloud Storage
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
    GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
    
    # La URL de los medios se construye a partir del nombre del bucket
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Se mantiene por si se usa localmente
else:
    # Configuración local (como estaba antes)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIÓN DE CORREO ELECTRÓNICO ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '998661114a@gmail.com') # Usar variable de entorno
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'stjgvletuhhnmuro') # Usar variable de entorno
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CONADIS_DISCOUNT_PERCENTAGE = 20

# --- CONFIGURACIÓN COMPLETA DE JAZZMIN ---
JAZZMIN_SETTINGS = {
    # ... (Tus configuraciones generales de site_title, site_header, etc.) ...
    "site_title": "Ticket World Admin",
    "site_header": "Ticket World",
    "site_brand": "Ticket World",
    "welcome_sign": "Bienvenido al Panel de Administración de Ticket World",
    "home_url": "admin:index", # El index estándar
    "home_icon": "fas fa-home",

    # TOP MENU LINKS (Se mantiene igual)
    "topmenu_links": [
        {"name": "Ir a la Web", "url": "/", "new_window": True, "icon": "fas fa-globe"},
        {"name": "Soporte Jazzmin", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True, "icon": "fas fa-life-ring"},
        {
            "name": "Notificaciones de Admin",
            "url": "admin:tickets_adminnotification_changelist",
            "icon": "fas fa-bell",
            # Las propiedades "badge" y "badge_color" las maneja custom_admin.js
        },
    ],

    # SIDE MENU (BARRA LATERAL IZQUIERDA)
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [], # Dejar vacío, ya que order_with_respect_to es más específico
    "hide_models": ["tickets.adminnotification"], # <-- ¡USAR ESTO PARA OCULTAR Notificaciones de Admin!

    # --- ¡CAMBIO CRÍTICO AQUÍ! VOLVEMOS A "main" PARA sidebar ---
    "sidebar": [
        # La directiva "main" generará todas las aplicaciones y modelos.
        # El orden de TODO el menú será controlado por 'order_with_respect_to'.
        "main", 
    ],

    # --- ORDEN EXACTO DEL MENÚ LATERAL SEGÚN TU SOLICITUD (¡USANDO order_with_respect_to!) ---
    # Esta lista es la fuente principal para la ordenación de TODO el menú lateral.
    # Los nombres de los custom links (como "Eventos Pendientes de Aprobación") DEBEN COINCIDIR EXACTAMENTE
    # con el "name" definido en el diccionario "custom_links".
    "order_with_respect_to": [
        # 1. REPORTS (App) - El nombre de la app
        "reports", 

        # 2. USUARIOS (App) - y sus elementos en el orden solicitado
        "usuarios", # El nombre de la app
        "usuarios.usuario", # 2.1 Usuarios (modelo)
        "usuarios.solicitudproveedor", # 2.2 Solicitud de Proveedores (modelo)
        "Solicitudes de Proveedores por Aprobar", # 2.3 Custom link (¡Nombre exacto del enlace!)
        "usuarios.usernotification", # 2.4 Notificaciones de usuarios (modelo)

        # 3. TICKETS (App) - y sus elementos en el orden solicitado
        "tickets", # El nombre de la app
        "Eventos Pendientes de Aprobación", # 3.1 Custom link (¡Nombre exacto del enlace!)
        "tickets.evento", # 3.2 Eventos (modelo)
        "tickets.categoria", # 3.3 Categorias (modelo)
        "tickets.venta", # 3.4 Ventas (modelo)
        "tickets.opinion", # 3.5 Opiniones (modelo)
        # 3.6 Notificaciones de admin (tickets.adminnotification) - Será ocultado por hide_models
        "tickets.metodopago", # 3.7 Metodos de pago (modelo)

        # Lo demás (Autenticación y autorización) - al final
        "auth", # La app de autenticación
        "auth.user", # Modelo de Usuario de Django
        "auth.Group", # Modelo de Grupo de Django
    ],

    # CUSTOM LINKS (Enlaces personalizados ADJUNTOS a las APPS - Se mantiene el formato)
    "custom_links": {
        "usuarios": [ 
            {
                "name": "Solicitudes de Proveedores por Aprobar", # <-- ¡Este nombre debe coincidir con order_with_respect_to!
                "url": "/admin/usuarios/solicitudproveedor/?aprobado__exact=0&q=",
                "icon": "fas fa-truck-loading",
            },
        ],
        "tickets": [ 
            {
                "name": "Eventos Pendientes de Aprobación", # <-- ¡Este nombre debe coincidir con order_with_respect_to!
                "url": "/admin/tickets/evento/?aprobado__exact=0&q=",
                "icon": "fas fa-calendar-times",
            },
        ],
        # No hay custom_link para "reports" aquí porque 'reports' es una APP de nivel superior.
    },

    # ICONOS PERSONALIZADOS PARA APPS/MODELOS (Ya tiene todos los iconos que definimos)
    "icons": {
        "auth": "fas fa-users-cog",     
        "usuarios": "fas fa-user-circle", 
        "tickets": "fas fa-ticket-alt",   

        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "usuarios.solicitudproveedor": "fas fa-truck-moving", 
        "usuarios.usuario": "fas fa-id-card",
        "tickets.evento": "fas fa-calendar-alt",
        "tickets.venta": "fas fa-dollar-sign",
        "tickets.categoria": "fas fa-tags",
        "tickets.opinion": "fas fa-comment-dots",
        "tickets.metodopago": "fas fa-credit-card",
        "tickets.adminnotification": "fas fa-bell", # Icono para el modelo de notificación de Admin
        "usuarios.usernotification": "fas fa-envelope-open", 
        "reports": "fas fa-chart-line", # <-- ¡Icono para la app 'reports'!
        "reports.reportdashboard": "fas fa-chart-pie", # Icono para el modelo dummy ReportDashboard
    },
    
    "default_icon_parents": "fas fa-angle-right",
    "default_icon_children": "fas fa-circle",

    
    "custom_js": "admin_custom/custom_admin.js",

    "show_ui_builder": False,
}



# --- JAZZMIN UI TWEAKS ---
JAZZMIN_UI_TWEAKS = {
    "theme": "litera", 
    "dark_mode_theme": None, 

    "navbar_small_text": False,
    "navbar_classes": "navbar-light navbar-white", 

    "sidebar_classes": "main-sidebar elevation-1 sidebar-light-primary", 

    "sidebar_nav_small_text": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,

    "body_classes": "", 
    "brand_small_text": False,
    "footer_small_text": False,
    "no_navbar_border": False, 
    "accent": None, 

    "actions_sticky_top": True,
}

INTERNAL_IPS = [
    "127.0.0.1",
]
# settings.py
MAPS_API_KEY = os.getenv('MAPS_API_KEY')

# --- CONFIGURACIÓN DE LOGGING PARA DEPURACIÓN EN PRODUCCIÓN ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}