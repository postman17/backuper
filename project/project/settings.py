import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-&7*q&u%2yvxe7qr$u(ywepw!89xs#&xyzis+w(d-vbh-5$j58n"


DEBUG = True if os.environ.get("DEBUG", None) == "True" else False

ALLOWED_HOSTS = (
    [host.strip() for host in os.environ.get("ALLOWED_HOSTS").split(",")] if os.environ.get("ALLOWED_HOSTS") else []
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "django_celery_beat",
    "django_celery_results",
    # Apps
    "helpers",
    "core",
    "backup",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", ""),
        "USER": os.environ.get("POSTGRES_USER", ""),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    },
}


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR.parent, "static")


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_CHARFIELD_MAXLENGTH = 255


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_BROKER_URL = os.environ.get("BROKER_URL", "redis://redis/10")
# CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")


MASTER_SALT = os.environ.get("MASTER_SALT", "default")
MASTER_PASSWORD = os.environ.get("MASTER_PASSWORD", "default")


BACKUP_CLIENT_TEMP_STATE_LIFETIME_SECONDS = 60


PATH_TO_FILES_FORMAT = "uploads/documents/{date}/"
