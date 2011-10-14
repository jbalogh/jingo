# -*- coding: utf-8 -*-
"""Tests for the jingo's builtin helpers."""
from datetime import datetime
from collections import namedtuple

from jinja2 import Markup
from nose.tools import eq_

import jingo
from jingo import helpers


def render(s, context={}):
    t = jingo.env.from_string(s)
    return t.render(**context)


def test_f():
    s = render('{{ "{0} : {z}"|f("a", z="b") }}')
    eq_(s, 'a : b')


def test_fe_helper():
    context = {'var': '<bad>'}
    template = '{{ "<em>{t}</em>"|fe(t=var) }}'
    eq_('<em>&lt;bad&gt;</em>', render(template, context))


def test_fe_positional():
    context = {'var': '<bad>'}
    template = '{{ "<em>{0}</em>"|fe(var) }}'
    eq_('<em>&lt;bad&gt;</em>', render(template, context))


def test_fe_unicode():
    context = {'var': u'Français'}
    template = '{{ "Speak {0}"|fe(var) }}'
    eq_(u'Speak Français', render(template, context))


def test_fe_markup():
    context = {'var': Markup('<mark>safe</mark>')}
    template = '{{ "<em>{0}</em>"|fe(var) }}'
    eq_('<em><mark>safe</mark></em>', render(template, context))
    template = '{{ "<em>{t}</em>"|fe(t=var) }}'
    eq_('<em><mark>safe</mark></em>', render(template, context))


def test_nl2br():
    text = "some\ntext\n\nwith\nnewlines"
    s = render('{{ x|nl2br }}', {'x': text})
    eq_(s, "some<br>text<br><br>with<br>newlines")

    text = None
    s = render('{{ x|nl2br }}', {'x': text})
    eq_(s, '')


def test_datetime():
    time = datetime(2009, 12, 25, 10, 11, 12)
    s = render('{{ d|datetime }}', {'d': time})
    eq_(s, 'December 25, 2009')

    s = render('{{ d|datetime("%Y-%m-%d %H:%M:%S") }}', {'d': time})
    eq_(s, '2009-12-25 10:11:12')

    s = render('{{ None|datetime }}')
    eq_(s, '')


def test_datetime_unicode():
    fmt = u"%Y 年 %m 月 %e 日"
    helpers.datetime(datetime.now(), fmt)


def test_ifeq():
    eq_context = {'a': 1, 'b': 1}
    neq_context = {'a': 1, 'b': 2}

    s = render('{{ a|ifeq(b, "<b>something</b>") }}', eq_context)
    eq_(s, '<b>something</b>')

    s = render('{{ a|ifeq(b, "<b>something</b>") }}', neq_context)
    eq_(s, '')


def test_class_selected():
    eq_context = {'a': 1, 'b': 1}
    neq_context = {'a': 1, 'b': 2}

    s = render('{{ a|class_selected(b) }}', eq_context)
    eq_(s, 'class="selected"')

    s = render('{{ a|class_selected(b) }}', neq_context)
    eq_(s, '')


def test_csrf():
    s = render('{{ csrf() }}', {'csrf_token': 'fffuuu'})
    eq_(s, "<div style='display:none'>"
           "<input type='hidden' name='csrfmiddlewaretoken' value='fffuuu' />"
           "</div>")


def test_field_attrs():
    class field(object):
        def __init__(self):
            self.field = namedtuple('_', 'widget')
            self.field.widget = namedtuple('_', 'attrs')
            self.field.widget.attrs = {'class': 'foo'}

        def __str__(self):
            attrs = self.field.widget.attrs
            attr_str = ' '.join('%s="%s"' % (k, v)
                                for (k, v) in attrs.iteritems())
            return Markup('<input %s />' % attr_str)

    f = field()
    s = render('{{ field|field_attrs(class="bar",name="baz") }}',
               {'field': f})
    eq_(s, '<input class="bar" name="baz" />')

def test_url():
    # urls defined in jingo/tests/urls.py
    s = render('{{ url("url-args", 1, "foo") }}')
    eq_(s, "/url/1/foo/")
    s = render('{{ url("url-kwargs", word="bar", num=1) }}')
    eq_(s, "/url/1/bar/")
