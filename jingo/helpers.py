# coding: utf-8

from __future__ import unicode_literals, print_function

from django.utils import six
from django.utils.translation import ugettext as _
from django.template.defaulttags import CsrfTokenNode
try:
    from django.utils.encoding import smart_unicode as smart_text
except ImportError:
    from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse

import jinja2

from jingo import register


@register.function
@jinja2.contextfunction
def csrf(context):
    """Equivalent of Django's ``{% crsf_token %}``."""
    return jinja2.Markup(CsrfTokenNode().render(context))


@register.filter
def f(string, *args, **kwargs):
    """
    Uses ``str.format`` for string interpolation.

    >>> {{ "{0} arguments and {x} arguments"|f('positional', x='keyword') }}
    "positional arguments and keyword arguments"
    """
    return string.format(*args, **kwargs)


@register.filter
def fe(string, *args, **kwargs):
    """Format a safe string with potentially unsafe arguments, then return a
    safe string."""

    string = six.text_type(string)

    args = [jinja2.escape(smart_text(v)) for v in args]

    for k in kwargs:
        kwargs[k] = jinja2.escape(smart_text(kwargs[k]))

    return jinja2.Markup(string.format(*args, **kwargs))


@register.filter
def nl2br(string):
    """Turn newlines into <br>."""
    if not string:
        return ''
    return jinja2.Markup('<br>'.join(jinja2.escape(string).splitlines()))


@register.filter
def datetime(t, fmt=None):
    """Call ``datetime.strftime`` with the given format string."""
    if fmt is None:
        fmt = _(u'%B %e, %Y')
    if not six.PY3:
        # The datetime.strftime function strictly does not
        # support Unicode in Python 2 but is Unicode only in 3.x.
        fmt = fmt.encode('utf-8')
    return smart_text(t.strftime(fmt)) if t else ''


@register.filter
def ifeq(a, b, text):
    """Return ``text`` if ``a == b``."""
    return jinja2.Markup(text if a == b else '')


@register.filter
def class_selected(a, b):
    """Return ``'class="selected"'`` if ``a == b``."""
    return ifeq(a, b, 'class="selected"')


@register.filter
def field_attrs(field_inst, **kwargs):
    """Adds html attributes to django form fields"""
    field_inst.field.widget.attrs.update(kwargs)
    return field_inst


@register.function(override=False)
def url(viewname, *args, **kwargs):
    """Return URL using django's ``reverse()`` function."""
    return reverse(viewname, args=args, kwargs=kwargs)
