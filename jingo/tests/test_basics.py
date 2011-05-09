import jinja2

from nose.tools import eq_
from mock import Mock, patch, sentinel

import jingo
import jinja2


@patch('jingo.env')
def test_render(mock_env):
    mock_template = jinja2.environment.Template('foo')
    mock_env.get_template.return_value = mock_template

    response = jingo.render(Mock(), sentinel.template, status=32)
    eq_('foo', response.content)
    mock_env.get_template.assert_called_with(sentinel.template)

    eq_(response.status_code, 32)


@patch('jingo.env')
def test_render_to_string(mock_env):
    template = jinja2.environment.Template('The answer is {{ answer }}')
    rendered = jingo.render_to_string(Mock(), template, {'answer': 42})

    eq_(rendered, 'The answer is 42')


def test_render_with_Template():
    template = jinja2.Environment().from_string('xxx')
    response = jingo.render(Mock(), template)
    eq_(response.content, 'xxx')


@patch('jingo.env.get_template')
def test_inclusion_tag(get_template):
    @jingo.register.inclusion_tag('xx.html')
    def tag(x):
        return {'z': x}
    get_template.return_value = jinja2.environment.Template('<{{ z }}>')
    t = jingo.env.from_string('{{ tag(1) }}')
    eq_('<1>', t.render())
