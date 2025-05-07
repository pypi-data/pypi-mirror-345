import os
from pathlib import Path

import structlog
from dotenv import load_dotenv

from meshadmin.server.project.logging import configure_structlog, setup_logging

load_dotenv()

logger = structlog.get_logger(__name__)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("MESHSERVER_SECRET_KEY")


def str2bool(v):
    return v.lower() in (
        "yes",
        "true",
        "t",
        "1",
    )


USE_X_FORWARDED_HOST = str2bool(os.getenv("MESHSERVER_USE_X_FORWARDED_HOST", "False"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str2bool(os.getenv("MESHSERVER_DEBUG", "False"))

ALLOWED_HOSTS = os.getenv("MESHSERVER_ALLOWED_HOSTS", "localhost").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv(
    "MESHSERVER_CSRF_TRUSTED_ORIGINS", "http://localhost:8000"
).split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "meshadmin.server.networks",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.openid_connect",
    "django_tailwind_cli",
    "django_cotton",
    "django_htmx",
    "django.contrib.sites",
]

MIDDLEWARE = [
    "django_structlog.middlewares.RequestMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "meshadmin.server.project.middleware.BreadcrumbMiddleware",
]

ROOT_URLCONF = "meshadmin.server.project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "meshadmin.server.project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("MESHSERVER_SQLITE_PATH", "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Zurich"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATICFILES_DIRS = [BASE_DIR / "static"]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "keycloak",
                "name": "Keycloak",
                "client_id": os.getenv("KEYCLOAK_CLIENT_ID", "meshadmin"),
                "secret": os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
                "settings": {
                    "server_url": os.getenv(
                        "KEYCLOAK_SERVER_URL",
                        "http://localhost:8080/realms/meshadmin/.well-known/openid-configuration",
                    ),
                },
            }
        ]
    }
}
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ONLY = True
LOGIN_URL = "/accounts/oidc/keycloak/login/?process=login"

# https://django-cotton.com/docs/configuration
COTTON_DIR = "components"

MESH_SERVER_URL = os.getenv("MESH_SERVER_URL", "http://localhost:8000")

KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "meshadmin")
KEYCLOAK_ADMIN_CLIENT = os.getenv("KEYCLOAK_ADMIN_CLIENT", "admin-cli")
KEYCLOAK_ISSUER = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_DEVICE_AUTH_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/auth/device"
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"
KEYCLOAK_CERTS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

PAGINATION_PER_PAGE = 25

# Logging
# configure_structlog()
# LOGGING = setup_logging()
