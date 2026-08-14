SECRET_KEY = "evoshield-test-secret-key"

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "backend.modules.M01_input_acquisition_validation",
]

MIDDLEWARE = []

ROOT_URLCONF = "test_urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

STATIC_URL = "static/"