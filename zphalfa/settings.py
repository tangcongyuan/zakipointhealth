"""
Django settings for zphalfa project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, time
from logging import handlers
import logging

VERSION_STAMP =  int(time.mktime(time.gmtime()))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e4$4j(15bgw%^y66pa(x)ut*k3a7%fw_*qj(1k3)j)hv2^65v1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
LOGIN_URL = '/signin'  # login_required redirects here if need be, setting up ?next= param usefully
SITE_ID = 1

ga_codes = {
    'alfa-dev.zakipointhealth.com': 'UA-60665302-2',
    'alpha.zakipointhealth.com': 'UA-60665302-3',
    'default': 'UA-60665302-51', # This number does not exist. Send analytics info into the ether.
}

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'django_extensions',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'zphalfa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+'/home/templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
        },
    },
]

WSGI_APPLICATION = 'zphalfa.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zphalfa',
        'USER': 'zph_django',
        'PASSWORD': 'dj2015',
        'HOST': 'localhost',
        'PORT': '',
    },
    'mongo': {
        'HOST': 'localhost',
        'PORT': 27017,
        'NAME': 'dev',
    },

}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'
USE_TZ = True

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

LOG_FILENAME = HOME_DIR+'/logs/zakipoint.log'

# Add the log message handler to the logger
handler = handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=250000, backupCount=5)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to handler
handler.setFormatter(formatter)

# Set up a specific logger with our desired output level
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
"""
"""

# Mail server related config
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'eric.tang@zakipoint.com'
EMAIL_HOST_PASSWORD = 'zakipoint'
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


