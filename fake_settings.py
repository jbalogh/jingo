import os

path = lambda *a: os.path.join(ROOT, *a)

ROOT = os.path.dirname(os.path.abspath(__file__))
INSTALLED_APPS = (
    'django.contrib.admin.apps.SimpleAdminConfig',
    'jingo.tests.jinja_app',
    'jingo.tests.django_app',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.auth',
)
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (path('jingo/tests/templates'),)
JINGO_EXCLUDE_APPS = ('django_app',)
ROOT_URLCONF = 'jingo.tests.urls'

SECRET_KEY = 'jingo'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path('jingo/tests/templates'),],
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'jingo.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
