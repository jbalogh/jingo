import os

import nose
import django

NAME = os.path.basename(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.dirname(__file__))

os.environ['DJANGO_SETTINGS_MODULE'] = 'fake_settings'
os.environ['PYTHONPATH'] = os.pathsep.join([ROOT,
                                            os.path.join(ROOT, 'examples')])

import django
if hasattr(django, 'setup'):
    django.setup()

from django.contrib.contenttypes.models import ContentType

if __name__ == '__main__':
    nose.main()
