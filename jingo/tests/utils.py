from django.test.html import HTMLParseError, parse_html
from nose.tools import eq_

from jingo import get_env


def htmleq_(html1, html2, msg=None):
    """
    Asserts that two HTML snippets are semantically the same.
    Whitespace in most cases is ignored, and attribute ordering is not
    significant. The passed-in arguments must be valid HTML.

    See ticket 16921: https://code.djangoproject.com/ticket/16921

    """
    dom1 = assert_and_parse_html(html1, msg,
                                 'First argument is not valid HTML:')
    dom2 = assert_and_parse_html(html2, msg,
                                 'Second argument is not valid HTML:')

    eq_(dom1, dom2)


def assert_and_parse_html(html, user_msg, msg):
    try:
        dom = parse_html(html)
    except HTMLParseError as e:
        standard_msg = '%s\n%s\n%s' % (user_msg, msg, e.msg)
        raise AssertionError(standard_msg)
    return dom


def render(s, context={}):
    t = get_env().from_string(s)
    return t.render(context)
