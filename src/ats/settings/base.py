from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# --------------------------------------------------
# Paths & environment
# --------------------------------------------------

# Current file: src/ats/settings/base.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # points to ATS_Backend/

dotenv_path = BASE_DIR / ".env"  # .env is directly in ATS_Backend
load_dotenv(dotenv_path)

# --------------------------------------------------
# Core settings
# --------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# --------------------------------------------------
# Application definition
# --------------------------------------------------

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "django_celery_results",
    "corsheaders",

    # Core ATS apps
    "apps.users.apps.UsersConfig",
    "apps.companies.apps.CompaniesConfig",
    "apps.jobs.apps.JobsConfig",
    "apps.applications.apps.ApplicationsConfig",

    # Workflow / domain apps
    "apps.pipelines.apps.PipelinesConfig",
    "apps.offers.apps.OffersConfig",

    # Cross-cutting apps
    "apps.notifications.apps.NotificationsConfig",
    "apps.audit.apps.AuditConfig",

    # Shared
    "apps.common.apps.CommonConfig",

    # OTP & Email apps
    "apps.otp.apps.OtpConfig",
    "apps.emails.apps.EmailsConfig",

    #UI
    'drf_spectacular',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ats.urls"

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
    }
]

WSGI_APPLICATION = "ats.wsgi.application"

# --------------------------------------------------
# Database
# --------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# --------------------------------------------------
# Custom user model
# --------------------------------------------------

AUTH_USER_MODEL = "users.User"

# --------------------------------------------------
# Password validation
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# Internationalization
# --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# Static & media
# --------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# Default primary key
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# Django REST Framework (base defaults)
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", 100))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 7))
    ),
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY", "fallback-insecure-key"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Other defaults
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}


# --------------------------------------------------
# CORS (separate frontend)
# --------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True  # dev only

# --------------------------------------------------
# Email
# --------------------------------------------------

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
)

# --------------------------------------------------
# Celery
# --------------------------------------------------

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_RESULT_EXTENDED = True


# SPECTACULAR_SETTINGS = {
#     'TITLE': 'JobPortal API',
#     'DESCRIPTION': 'ATS Modules project with JWT Authentication',
#     'VERSION': '1.0.0',
#     'SERVE_INCLUDE_SCHEMA': False,
    
#     # Separation of Request/Response components 
#     'COMPONENT_SPLIT_REQUEST': True, 

#     # This adds the "Authorize" button to Swagger for your JWT tokens
#     'SECURITY': [{
#         'jwtAuth': [],
#     }],
#     'APPEND_COMPONENTS': {
#         'securitySchemes': {
#             'jwtAuth': {
#                 'type': 'http',
#                 'scheme': 'bearer',
#                 'bearerFormat': 'JWT',
#             }
#         }
#     },
# }