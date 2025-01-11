"""
Django settings for core project.
"""

import os
from pathlib import Path
from decouple import config, Csv

# --------------------------------------------
# Paths e diretórios base
# --------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------
# Segurança: SECRET_KEY e DEBUG
# --------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=False, cast=bool)

# --------------------------------------------
# Hosts e CSRF
# --------------------------------------------
ALLOWED_HOSTS = [
    'sistema-controle-funcionarios-nh19os4ym-msribeiro2010s-projects.vercel.app',
]
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-147e.up.railway.app',
    'http://web-production-147e.up.railway.app',
    # Se quiser adicionar o domínio do Vercel aqui, ex.:
    # 'https://sistema-controle-funcionarios-nh19os4ym-msribeiro2010s-projects.vercel.app',
]

# --------------------------------------------
# Apps instalados
# --------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App de funcionários
    'funcionarios.apps.FuncionariosConfig',

    # Bibliotecas de formulários e CSS
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --------------------------------------------
# Middlewares
# --------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise para servir estáticos em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------
# WhiteNoise - compressão e versionamento
# (Não sobrescreva com outra StaticFilesStorage!)
# --------------------------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --------------------------------------------
# URLs e WSGI
# --------------------------------------------
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# --------------------------------------------
# Banco de Dados - PostgreSQL
# --------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='controle_funcionarios'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='mar'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# --------------------------------------------
# Validação de senhas
# --------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# --------------------------------------------
# Internacionalização
# --------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --------------------------------------------
# Arquivos estáticos e mídia
# --------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Se tiver arquivos de mídia, acrescente também:
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------
# Primary key field
# --------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------
# Configurações de login/logout
# --------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# --------------------------------------------
# Logging (exemplo em console)
# --------------------------------------------
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
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# --------------------------------------------
# Segurança em produção
# --------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Se ocorrer loop infinito em Vercel, tente SECURE_SSL_REDIRECT = False
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------------------------------
# Sessão e CSRF
# --------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24h
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # Mude para True em produção com HTTPS

CSRF_COOKIE_SECURE = False  # Mude para True em produção com HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_AGE = 86400  # 24 horas
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
