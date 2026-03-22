from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.microsoft",
    "portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "cavazos_ai.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "portal" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "cavazos_ai.wsgi.application"
ASGI_APPLICATION = "cavazos_ai.asgi.application"
DB_PATH = os.getenv("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))
PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", "/data/projects"))
DEFAULT_SHARED_MEDIA_ROOT = Path("/data/shared") if Path("/data").exists() else BASE_DIR / "data" / "shared"
SHARED_MEDIA_ROOT = Path(os.getenv("SHARED_MEDIA_ROOT", str(DEFAULT_SHARED_MEDIA_ROOT)))
SHARED_MEDIA_MAX_UPLOAD_BYTES = int(os.getenv("SHARED_MEDIA_MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "orb-chat-ui"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = int(os.getenv("DJANGO_SITE_ID", "1"))
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# allauth baseline setup. Social providers (like Microsoft) can be configured by adding
# SocialApp entries in Django admin and optionally provider-specific settings.
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email", "password1*", "password2*"]
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_ADAPTER = "portal.adapters.PortalAccountAdapter"
SOCIALACCOUNT_ADAPTER = "portal.adapters.PortalSocialAccountAdapter"
MICROSOFT_ALLOWED_EMAILS = {
    email.strip().lower()
    for email in os.getenv("MICROSOFT_ALLOWED_EMAILS", "samuel@alshival.ai").split(",")
    if email.strip()
}
