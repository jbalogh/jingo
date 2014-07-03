# coding: utf-8

from __future__ import unicode_literals, print_function

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template.defaulttags import CsrfTokenNode
from django.utils import six
from django.utils.encoding import smart_str
try:
    from django.utils.encoding import smart_unicode as smart_text
except ImportError:
    from django.utils.encoding import smart_text
from django.utils.http import urlencode
from django.utils.translation import ugettext as _

import jinja2

from jingo import register


@register.function
@jinja2.contextfunction
def csrf(context):
    """Equivalent of Django's ``{% crsf_token %}``."""
    return jinja2.Markup(CsrfTokenNode().render(context))


@register.filter
def f(s, *args, **kwargs):
    """
    Uses ``str.format`` for string interpolation.

    **Note**: Always converts to s to text type before interpolation.

    >>> {{ "{0} arguments and {x} arguments"|f('positional', x='keyword') }}
    "positional arguments and keyword arguments"
    """
    s = six.text_type(s)
    return s.format(*args, **kwargs)


@register.filter
def fe(s, *args, **kwargs):
    """Format a safe string with potentially unsafe arguments, then return a
    safe string."""

    s = six.text_type(s)

    args = [jinja2.escape(smart_text(v)) for v in args]

    for k in kwargs:
        kwargs[k] = jinja2.escape(smart_text(kwargs[k]))

    return jinja2.Markup(s.format(*args, **kwargs))


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
    for k, v in kwargs.items():
        if v is not None:
            field_inst.field.widget.attrs[k] = v
        else:
            try:
                del field_inst.field.widget.attrs[k]
            except KeyError:
                pass
    return field_inst


@register.function(override=False)
def url(viewname, *args, **kwargs):
    """Return URL using django's ``reverse()`` function."""
    return reverse(viewname, args=args, kwargs=kwargs)


@register.filter
def urlparams(url_, fragment=None, query_dict=None, **query):
    """
Add a fragment and/or query parameters to a URL.

New query params will be appended to exising parameters, except duplicate
names, which will be replaced.
"""
    url_ = urlparse.urlparse(url_)
    fragment = fragment if fragment is not None else url_.fragment

    q = url_.query
    new_query_dict = (QueryDict(smart_str(q), mutable=True) if
                      q else QueryDict('', mutable=True))
    if query_dict:
        for k, l in query_dict.lists():
            new_query_dict[k] = None  # Replace, don't append.
            for v in l:
                new_query_dict.appendlist(k, v)

    for k, v in query.items():
        # Replace, don't append.
        if isinstance(v, list):
            new_query_dict.setlist(k, v)
        else:
            new_query_dict[k] = v

    query_string = urlencode([(k, v) for k, l in new_query_dict.lists() for
                              v in l if v is not None])
    new = urlparse.ParseResult(url_.scheme, url_.netloc, url_.path,
                               url_.params, query_string, fragment)
    return new.geturl()
