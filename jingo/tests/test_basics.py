from __future__ import unicode_literals

from django.shortcuts import render
import jinja2

from nose.tools import eq_
try:
    from unittest.mock import Mock, patch, sentinel
except ImportError:
    from mock import Mock, patch, sentinel

import jingo


@patch('jingo.get_env')
def test_render(mock_get_env):
    mock_template = Mock()
    mock_env = Mock()
    mock_env.get_template.return_value = mock_template
    mock_get_env.return_value = mock_env

    response = render(Mock(), sentinel.template, status=32)
    mock_env.get_template.assert_called_with(sentinel.template)
    assert mock_template.render.called

    eq_(response.status_code, 32)


@patch('jingo.get_env')
def test_render_to_string(mock_get_env):
    template = jinja2.environment.Template('The answer is {{ answer }}')
    rendered = jingo.render_to_string(Mock(), template, {'answer': 42})

    eq_(rendered, 'The answer is 42')


def test_inclusion_tag():
    @jingo.register.inclusion_tag('xx.html')
    def tag(x):
        return {'z': x}

    env = jingo.get_env()
    with patch.object(env, 'get_template') as mock_get_template:
        temp = jinja2.environment.Template('<{{ z }}>')
        mock_get_template.return_value = temp
        t = env.from_string('{{ tag(1) }}')
        eq_('<1>', t.render())
