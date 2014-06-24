from __future__ import unicode_literals

import django
from django.shortcuts import render

import jinja2
from nose.tools import eq_
try:
    from unittest.mock import Mock, patch, sentinel
except ImportError:
    from mock import Mock, patch, sentinel

import jingo


def setup_module():
    if hasattr(django, 'setup'):
        django.setup()


@patch('jingo.env')
def test_render(mock_env):
    mock_template = Mock()
    mock_env.get_template.return_value = mock_template

    response = render(Mock(), sentinel.template, status=32)
    mock_env.get_template.assert_called_with(sentinel.template)
    assert mock_template.render.called

    eq_(response.status_code, 32)


@patch('jingo.env')
def test_render_to_string(mock_env):
    template = jinja2.environment.Template('The answer is {{ answer }}')
    rendered = jingo.render_to_string(Mock(), template, {'answer': 42})

    eq_(rendered, 'The answer is 42')


@patch('jingo.env.get_template')
def test_inclusion_tag(get_template):
    @jingo.register.inclusion_tag('xx.html')
    def tag(x):
        return {'z': x}
    get_template.return_value = jinja2.environment.Template('<{{ z }}>')
    t = jingo.env.from_string('{{ tag(1) }}')
    eq_('<1>', t.render())
