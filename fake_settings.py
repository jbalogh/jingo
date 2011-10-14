import os

path = lambda *a: os.path.join(ROOT, *a)

ROOT = os.path.dirname(os.path.abspath(__file__))
INSTALLED_APPS = (
    'jingo.tests.jinja_app',
    'jingo.tests.django_app',
)
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (path('jingo/tests/templates'),)
JINGO_EXCLUDE_APPS = ('django_app',)
ROOT_URLCONF = 'jingo.tests.urls'