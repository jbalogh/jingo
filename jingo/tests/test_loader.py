from django.shortcuts import render

from nose.tools import eq_
from mock import Mock

from jingo import get_env


def test_render():
    r = render(Mock(), 'jinja_app/test.html', {})
    eq_(r.content, 'HELLO')


def test_render_django():
    r = render(Mock(), 'django_app/test.html', {})
    eq_(r.content, 'HELLO ...\n')

