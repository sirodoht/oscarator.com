"""
Django settings for oscarator project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path
from urllib import parse

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "im_a_secret_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get("DEBUG") == "1" else False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "oscarator.com"]

ADMINS = [("Theodore Keloglou", "zf@sirodoht.com")]


# Application definition

INSTALLED_APPS = [
    "main.apps.MainConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "main.middleware.AnalyticsMiddleware",
]

ROOT_URLCONF = "oscarator.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.quotes_processor",
            ]
        },
    }
]

WSGI_APPLICATION = "oscarator.wsgi.application"

LOGIN_URL = "/enter"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

database_url = os.environ.get("DATABASE_URL", "")
database_url = parse.urlparse(database_url)
# e.g. postgres://mataroa:password@127.0.0.1:5432/mataroa
database_name = database_url.path[1:]  # url.path is '/mataroa'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parse.unquote(database_name or ""),
        "USER": parse.unquote(database_url.username or ""),
        "PASSWORD": parse.unquote(database_url.password or ""),
        "HOST": database_url.hostname,
        "PORT": database_url.port or "",
        "CONN_MAX_AGE": 500,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email
# https://docs.djangoproject.com/en/2.1/topics/email/

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "email-smtp.eu-west-1.amazonaws.com"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = "Oscar Wild <wild@oscarator.com>"
EMAIL_FROM_HOST = "oscarator.org"
SERVER_EMAIL = "Oscar Server <server@oscarator.org>"
EMAIL_SUBJECT_PREFIX = "[oscarator] "


# Security middleware
# https://docs.djangoproject.com/en/2.1/ref/middleware/#module-django.middleware.security

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

CURRENT_YEAR = 2022
VOTING_ENABLED = True
