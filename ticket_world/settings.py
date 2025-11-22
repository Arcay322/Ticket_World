# settings.py

"""
Django settings for ticket_world project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
from decouple import config

# Cargar variables de entorno desde .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-4o4waal&@#kcb0s&)@f00-e3&t#v7ic-cf)2n57%e95au1@nl+')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Añadir el hostname de Render a ALLOWED_HOSTS si está disponible
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    # --- JAZZMIN START ---
    'jazzmin',
    # --- JAZZMIN END ---

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'corsheaders',
    'cloudinary_storage', # Cloudinary Storage
    'cloudinary',         # Cloudinary

    # Local apps
    'ticket_world',
    'usuarios',
    'tickets',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ticket_world.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
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
LOGIN_REDIRECT_URL = '/inicio/'
LOGOUT_REDIRECT_URL = 'login'

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
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CONFIGURACIÓN DE CLOUDINARY (MEDIA FILES) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dc1hk7zix',
    'API_KEY': '569991529844796',
    'API_SECRET': '_gFRhUFu7eV_HHWKtu521Dmrmik',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'  # Cloudinary handles the URL generation
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIÓN DE CORREO ELECTRÓNICO ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '998661114a@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'stjgvletuhhnmuro')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CONADIS_DISCOUNT_PERCENTAGE = 20

# --- CONFIGURACIÓN COMPLETA DE JAZZMIN ---
JAZZMIN_SETTINGS = {
    "site_title": "Ticket World Admin",
    "site_header": "Ticket World",
    "site_brand": "Ticket World",
    "welcome_sign": "Bienvenido al Panel de Administración de Ticket World",
    "home_url": "admin:index",
    "home_icon": "fas fa-home",

    "topmenu_links": [
        {"name": "Ir a la Web", "url": "/", "new_window": True, "icon": "fas fa-globe"},
        {"name": "Soporte Jazzmin", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True, "icon": "fas fa-life-ring"},
        {
            "name": "Notificaciones de Admin",
            "url": "admin:tickets_adminnotification_changelist",
            "icon": "fas fa-bell",
        },
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": ["tickets.adminnotification"],

    "sidebar": [
        "main", 
    ],

    "order_with_respect_to": [
        "reports", 
        "usuarios",
        "usuarios.usuario",
        "usuarios.solicitudproveedor",
        "Solicitudes de Proveedores por Aprobar",
        "usuarios.usernotification",
        "tickets",
        "Eventos Pendientes de Aprobación",
        "tickets.evento",
        "tickets.categoria",
        "tickets.venta",
        "tickets.opinion",
        "tickets.metodopago",
        "auth",
        "auth.user",
        "auth.Group",
    ],

    "custom_links": {
        "usuarios": [ 
            {
                "name": "Solicitudes de Proveedores por Aprobar",
                "url": "/admin/usuarios/solicitudproveedor/?aprobado__exact=0&q=",
                "icon": "fas fa-truck-loading",
            },
        ],
        "tickets": [ 
            {
                "name": "Eventos Pendientes de Aprobación",
                "url": "/admin/tickets/evento/?aprobado__exact=0&q=",
                "icon": "fas fa-calendar-times",
            },
        ],
    },

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
        "tickets.adminnotification": "fas fa-bell",
        "usuarios.usernotification": "fas fa-envelope-open", 
        "reports": "fas fa-chart-line",
        "reports.reportdashboard": "fas fa-chart-pie",
    },
    
    "default_icon_parents": "fas fa-angle-right",
    "default_icon_children": "fas fa-circle",
    "custom_js": "admin_custom/custom_admin.js",
    "show_ui_builder": False,
}

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

MAPS_API_KEY = os.getenv('MAPS_API_KEY')

# Logging
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