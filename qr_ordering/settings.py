from pathlib import Path
import os
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")  

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.humanize',

    'core',
    'menu',
    'inventory',
    'orders',
    'payments',
    'reports',
    'analytics',
    'accounts',
    'feedback',
]

JAZZMIN_SETTINGS = {
    "site_title": "QR Café Admin",
    "site_header": "QR Café Admin",
    "site_brand": "QR Café",
    "welcome_sign": "Welcome to QR Café Admin",
    "copyright": "QR Café",
    "show_ui_builder": False,
    "hide_apps": [],
    "icons": {
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "menu.item": "fas fa-burger",
        "orders.order": "fas fa-receipt",
        "orders.orderitem": "fas fa-list",
        "inventory.inventoryitem": "fas fa-boxes-stacked",
        "reports": "fas fa-chart-column",
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qr_ordering.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': { 'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'qr_ordering.wsgi.application'

DATABASES = { 'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# at bottom (or wherever your settings live)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

WEATHER_DEFAULT_CITY = 'Bengaluru'
WEATHER_DEFAULT_LAT = 12.9716
WEATHER_DEFAULT_LON = 77.5946
