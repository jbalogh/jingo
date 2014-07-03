from __future__ import unicode_literals

import django
from django import forms
from django.utils import six

from jinja2 import escape
from nose.tools import eq_

from .utils import render


class MyForm(forms.Form):
    email = forms.EmailField()


def test_monkey_patch():
    form = MyForm()
    html = form.as_ul()
    context = {'form': form}
    t = '{{ form.as_ul() }}'

    if django.VERSION < (1, 7):
        eq_(escape(html), render(t, context))

        import jingo.monkey
        jingo.monkey.patch()

    eq_(html, render(t, context))

    s = six.text_type(form['email'])
    eq_(s, render('{{ form.email }}', {'form': form}))
