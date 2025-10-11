from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallbackkey1234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

AUTH_USER_MODEL = 'accounts.CustomProfiles'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',
    'accounts',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.mfa',
    'widget_tweaks',
    'django.contrib.humanize',
    'allauth.usersessions',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'allauth.usersessions.middleware.UserSessionsMiddleware',
]

ROOT_URLCONF = 'allauth_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.EmailOrUserNameModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'allauth_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': BASE_DIR / config('DATABASE_NAME', default='db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('TIME_ZONE', default='Asia/Kathmandu')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm'
}

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_BLACKLIST = ['admin']
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",
    "signup": "3/h",
    "password_reset": "10/h",
}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS = 4
ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 120
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = config('ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS', default=1, cast=int)
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = config('ACCOUNT_DEFAULT_HTTP_PROTOCOL', default='http')
ACCOUNT_LOGIN_ON_PASSWORD_RESET = False
ACCOUNT_REAUTHENTICATION_TIMEOUT = 300
ACCOUNT_EMAIL_SUBJECT_PREFIX = config('ACCOUNT_EMAIL_SUBJECT_PREFIX', default='[MYAUTHALL]')
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
PASSWORD_RESET_TIMEOUT = 3600
ACCOUNT_PASSWORD_RESET_TIMEOUT = PASSWORD_RESET_TIMEOUT

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@myauthall.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@myauthall.com')

# Sites framework
SITE_ID = 1
SITE_NAME = config('SITE_NAME', default='MYAUTHALL')



# Celery settings
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'allauth.account': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
        'allauth.socialaccount': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
        'django.request': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
        'urllib3': {'handlers': ['console'], 'level': 'DEBUG'},
        'accounts': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
    },
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': "online"},
        'OAUTH_PKCE_ENABLED': True,
    },
    'github': {
        'SCOPE': ['user', 'repo', 'read:org'],
        'VERIFIED_EMAIL': True,
    },
}