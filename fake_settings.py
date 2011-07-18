import os

path = lambda *a: os.path.join(ROOT, *a)

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader'
)
TEMPLATE_DIRS = (path('jingo/tests/templates'))
DJANGO_TEMPLATE_APPS = 'django_app'
