from django import forms

from jinja2 import escape
from nose.tools import eq_

import jingo
import jingo.monkey


def render(s, context=None):
    t = jingo.env.from_string(s)
    return t.render(context or {})


class MyForm(forms.Form):
    email = forms.EmailField()


def test_monkey_patch():
    form = MyForm()
    html = form.as_ul()
    context = {'form': form}
    t = '{{ form.as_ul() }}'

    eq_(escape(html), render(t, context))

    jingo.monkey.patch()
    eq_(html, render(t, context))
