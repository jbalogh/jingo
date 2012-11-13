from django.utils import translation
from django.views.generic.simple import direct_to_template

from mock import patch, sentinel
from nose.tools import eq_

from jingo import get_env, render_to_string


def test_direct_to_template():
    response = direct_to_template(sentinel.request,
                                  'jinja_app/test_nonoverride.html',
                                  {'x': 1})
    eq_('HELLO', response.content)


def test_template_substitution_crash():
    translation.activate('xx')

    env = get_env()

    # The localized string has the wrong variable name in it
    s = '{% trans string="heart" %}Broken {{ string }}{% endtrans %}'
    template = env.from_string(s)
    rendered = render_to_string(sentinel.request, template, {})
    eq_(rendered, 'Broken heart')
