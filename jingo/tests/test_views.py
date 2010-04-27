from django.utils import translation
from mock import Mock, patch, sentinel

import jinja2
from nose.tools import eq_
from test_helpers import render

import jingo.views
from jingo import get_env


@patch('jingo.render')
def test_direct_to_template(mock_render):
    request = sentinel.request
    jingo.views.direct_to_template(request, 'base.html', x=1)
    mock_render.assert_called_with(request, 'base.html', {'x': 1})


def test_template_substitution_crash():
    translation.activate('xx')

    env = get_env()

    # The localized string has the wrong variable name in it
    s = '{% trans string="heart" %}Broken {{ string }}{% endtrans %}'
    template = env.from_string(s)
    rendered = jingo.render_to_string(Mock(), template, {})
    eq_(rendered, 'Broken heart')
