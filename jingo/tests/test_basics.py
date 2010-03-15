from nose.tools import eq_
from mock import Mock, patch, sentinel

import jingo
import jinja2


@patch('jingo.env')
def test_render(mock_env):
    mock_template = Mock()
    mock_env.get_template.return_value = mock_template

    response = jingo.render(Mock(), sentinel.template, status=32)
    mock_env.get_template.assert_called_with(sentinel.template)
    assert mock_template.render.called

    eq_(response.status_code, 32)


@patch('jingo.env')
def test_render_to_string(mock_env):
    template = jinja2.environment.Template('The answer is {{ answer }}')
    rendered = jingo.render_to_string(Mock(), template, {'answer': 42})

    eq_(rendered, 'The answer is 42')
