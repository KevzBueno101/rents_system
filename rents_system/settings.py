from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts'
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

ROOT_URLCONF = 'rents_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'accounts/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.admin_profile',  # Legacy - kept for compatibility
                'accounts.context_processors.user_profile',  # Enhanced unified profile
                'accounts.context_processors.system_stats',   # System statistics
                'accounts.context_processors.recent_activity', # Recent activity feed
                'accounts.context_processors.recent_payments', # Recent payments feed
                'accounts.context_processors.notifications',   # Notification system
                'accounts.context_processors.app_settings',   # App metadata
            ],
        },
    },
]

WSGI_APPLICATION = 'rents_system.wsgi.application'

import dj_database_url

USE_POSTGRES = os.getenv('USE_POSTGRES', 'false').strip().lower() == 'true'

if USE_POSTGRES and os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql' if USE_POSTGRES else 'django.db.backends.mysql',
            'NAME': os.getenv('PG_DB_NAME', 'rents_db_pg') if USE_POSTGRES else os.getenv('DB_NAME', 'rents_db'),
            'USER': os.getenv('PG_USER', 'postgres') if USE_POSTGRES else os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('PG_PASSWORD', '') if USE_POSTGRES else os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('PG_HOST', 'localhost') if USE_POSTGRES else os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('PG_PORT', '5432') if USE_POSTGRES else os.getenv('DB_PORT', '3306'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration for Password Reset
# Use Gmail SMTP as primary for immediate working solution
if os.getenv('EMAIL_HOST_USER') and os.getenv('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'RENTS System <noreply@rents.com>')
elif os.getenv('SENDGRID_API_KEY'):
    # SendGrid as fallback
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
    DEFAULT_FROM_EMAIL = os.getenv('FROM_EMAIL', 'RENTS System <noreply@rents.com>')
else:
    # Console for testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'RENTS System <noreply@rents.com>'

# Password Reset Settings
PASSWORD_RESET_TIMEOUT = 86400  # 24 hours in seconds

# Site Configuration for Password Reset Links
SITE_ID = 1

# Domain configuration for password reset links
if os.getenv('RENDER'):
    # Production: Use Render domain
    SITE_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://rents-system.onrender.com')
else:
    # Development: Use localhost
    SITE_URL = 'http://127.0.0.1:8000'

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
