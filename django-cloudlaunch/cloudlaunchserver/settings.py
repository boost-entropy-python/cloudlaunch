"""
Django settings for cloudlaunch project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# Django site id
SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CHANGEthisONinstall'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = False
LOGIN_REDIRECT_URL = "/catalog"

# Begin: django-cors-headers settings
CORS_ORIGIN_ALLOW_ALL = True

# Django filters out headers with an underscore by default, so make sure they
# have dashes instead.
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = default_headers + (
    'cl-credentials-id',
    'cl-os-username',
    'cl-os-password',
    'cl-os-tenant-name',
    'cl-os-project-name',
    'cl-os-project-domain-name',
    'cl-os-user-domain-name',
    'cl-os-identity-api-version',
    'cl-aws-access-key',
    'cl-aws-secret-key',
    'cl-azure-subscription-id'
    'cl-azure-client-id',
    'cl-azure-secret',
    'cl-azure-tenant',
    'cl-azure-resource-group',
    'cl-azure-storage-account',
    'cl-azure-vm-default-username',
    'cl-gcp-credentials-json',
)
# End: django-cors-headers settings

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Application definition

INSTALLED_APPS = [
    # Django auto complete light - for autocompleting foreign keys in admin
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'nested_admin',
    'corsheaders',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'djcloudbridge',
    'public_appliances',
    'cloudlaunch',
    # rest framework must come after cloudlaunch so templates can be overridden
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
    'django_countries',
    'django_filters',
    'polymorphic',
    'cloudlaunchserver'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloudlaunchserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'cloudlaunchserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.environ.get('CLOUDLAUNCH_DB_ENGINE', 'sqlite3'),
        'NAME': os.environ.get('CLOUDLAUNCH_DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
         # The following settings are not used with sqlite3:
        'USER': os.environ.get('CLOUDLAUNCH_DB_USER'),
        'HOST': os.environ.get('CLOUDLAUNCH_DB_HOST'), # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': os.environ.get('CLOUDLAUNCH_DB_PORT'), # Set to empty string for default.
        'PASSWORD': os.environ.get('CLOUDLAUNCH_DB_PASSWORD'),
    }
}


SITE_ID = 1

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = False

USE_L10N = True

USE_TZ = True


CLOUDLAUNCH_PATH_PREFIX = os.environ.get('CLOUDLAUNCH_PATH_PREFIX', '')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = CLOUDLAUNCH_PATH_PREFIX + '/static/'


# Installed apps settings

REST_FRAMEWORK = {
    'PAGE_SIZE': 50,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'cloudlaunch.authentication.TokenAuthentication'
    )
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'djcloudbridge.serializers.UserSerializer'
}
REST_AUTH_TOKEN_MODEL = 'cloudlaunch.models.AuthToken'
REST_AUTH_TOKEN_CREATOR = 'cloudlaunch.authentication.default_create_token'

REST_SESSION_LOGIN = True

REST_SCHEMA_BASE_URL = CLOUDLAUNCH_PATH_PREFIX + '/'

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
sentry_sdk.init(
    # dsn="https://<key>@sentry.io/<project>",
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()]
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(pathname)s:%(lineno)d - %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file-cloudlaunch': {
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'level': 'INFO',
            'filename': 'cloudlaunch.log',
        },
        'file-django': {
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'level': 'WARNING',
            'filename': 'cloudlaunch-django.log',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file-django'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django.db.backends': {
            'handlers': ['file-django'],
            'level': 'INFO',
        },
        'django.template': {
            'handlers': ['console', 'file-django'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'file-django'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cloudlaunch': {
            'handlers': ['console', 'file-cloudlaunch'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Allow settings to be overridden in a cloudlaunch/settings_local.py
try:
    from cloudlaunchserver.settings_local import *  # noqa
except ImportError:
    pass
