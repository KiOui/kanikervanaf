"""
Django settings for kanikervanaf project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from kanikervanaf.settings.base import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "oc&trhl=-2=$raqf^y4i07i-gfxg75l11i7#1oyb^tpbpu(5s%"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

RECAPTCHA_PUBLIC_KEY = "6Le_FNAUAAAAAJM1S2Q7vdZAfz9U79sdjP0y52XH"
RECAPTCHA_PRIVATE_KEY = "6Le_FNAUAAAAAKYHM-EVHUTq_A9SP4mbrlB0d7W4"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
