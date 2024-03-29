"""
Django settings for kanikervanaf project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from kanikervanaf.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["kanikervanaf.total5.nl", "kanikervanaf.nl"]

SESSION_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": int(os.environ.get("POSTGRES_PORT", 5432)),
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/kanikervanaf/log/django.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

if os.environ.get("GOOGLE_ANALYTICS_KEY"):
    GOOGLE_ANALYTICS_KEY = os.environ.get("GOOGLE_ANALYTICS_KEY")

if os.environ.get("DJANGO_EMAIL_HOST"):
    EMAIL_HOST = os.environ["DJANGO_EMAIL_HOST"]
    EMAIL_PORT = os.environ["DJANGO_EMAIL_PORT"]
    EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", False) == "True"
    EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", False) == "True"
    CUSTOMER_SERVICE_EMAIL = os.environ.get("DJANGO_CUSTOMER_SERVICE_EMAIL")

if os.environ.get("DJANGO_RECAPTCHA_PUBLIC_KEY") and os.environ.get(
    "DJANGO_RECAPTCHA_PRIVATE_KEY"
):
    RECAPTCHA_PUBLIC_KEY = os.environ["DJANGO_RECAPTCHA_PUBLIC_KEY"]
    RECAPTCHA_PRIVATE_KEY = os.environ["DJANGO_RECAPTCHA_PRIVATE_KEY"]
