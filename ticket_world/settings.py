# settings.py

"""
Django settings for ticket_world project.
... (el resto de los comentarios iniciales) ...
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Carga las variables del archivo .env al principio de todo
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4o4waal&@#kcb0s&)@f00-e3&t#v7ic-cf)2n57%e95au1@nl+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'tickets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ticket_world.wsgi.application'


# -------------------------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS (VERSIÓN FINAL Y SIMPLIFICADA)
# -------------------------------------------------------------------

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        # Busca la variable DATABASE_URL en el .env y la usa para configurar todo.
        default=os.environ.get('DATABASE_URL')
    )
}


# -------------------------------------------------------------------
# CONFIGURACIÓN DE AUTENTICACIÓN
# -------------------------------------------------------------------

# Le decimos a Django que use tu modelo personalizado de Usuario
AUTH_USER_MODEL = 'usuarios.Usuario'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/inicio/'
LOGOUT_REDIRECT_URL = 'login'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# -------------------------------------------------------------------
# INTERNACIONALIZACIÓN
# -------------------------------------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS Y DE MEDIOS
# -------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------------------------------------------------------
# OTRAS CONFIGURACIONES
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Email (asegúrate de que los datos sean correctos)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '998661114a@gmail.com'
EMAIL_HOST_PASSWORD = 'stjgvletuhhnmuro'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER