import os

import nose
import django

NAME = os.path.basename(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.dirname(__file__))

os.environ['DJANGO_SETTINGS_MODULE'] = 'fake_settings'
os.environ['PYTHONPATH'] = os.pathsep.join([ROOT,
                                            os.path.join(ROOT, 'examples')])

if __name__ == '__main__':
    if hasattr(django, 'setup'):
        # Django's app registry was added in 1.7. We need to call `setup` to
        # initiate it.
        django.setup()
    nose.main()
