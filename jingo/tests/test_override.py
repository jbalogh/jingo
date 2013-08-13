from os.path import join, dirname, pardir

from django.utils import six
from django.shortcuts import render_to_response
from django.test import TestCase
from django.test.utils import override_settings

@override_settings(TEMPLATE_LOADERS=('jingo.Loader',))
class TestOverrideSettings(TestCase):

    def test_no_override_template_dirs(self):
        response = render_to_response('test.html')
        self.assertEqual(response.content, b'TEST' if six.PY3 else 'TEST')

    @override_settings(TEMPLATE_DIRS=[join('jingo', 'tests', 'templates', 'templates_a')])
    def test_overridden_template_dirs(self):
        response = render_to_response('test_a.html')
        self.assertEqual(response.content, b'A' if six.PY3 else 'A')
