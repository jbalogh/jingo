"""Adapter for using Jinja2 with Django."""
import functools
import imp
import logging

from django import http
from django.conf import settings
from django.template.context import get_standard_processors
from django.utils.importlib import import_module
from django.utils.translation import trans_real

import jinja2

VERSION = (0, 3)
__version__ = '.'.join(map(str, VERSION))

log = logging.getLogger('jingo')


_helpers_loaded = False


class Environment(jinja2.Environment):

    def get_template(self, name, parent=None, globals=None):
        """Make sure our helpers get loaded before any templates."""
        load_helpers()
        return super(Environment, self).get_template(name, parent, globals)

    def from_string(self, source, globals=None, template_class=None):
        load_helpers()
        return super(Environment, self).from_string(source, globals,
                                                    template_class)


def get_env():
    """Configure and return a jinja2 Environment."""
    # Mimic Django's setup by loading templates from directories in
    # TEMPLATE_DIRS and packages in INSTALLED_APPS.
    x = ((jinja2.FileSystemLoader, settings.TEMPLATE_DIRS),
         (jinja2.PackageLoader, settings.INSTALLED_APPS))
    loaders = [loader(p) for loader, places in x for p in places]

    opts = {'trim_blocks': True,
            'extensions': ['jinja2.ext.i18n'],
            'autoescape': True,
            'auto_reload': settings.DEBUG,
            'loader': jinja2.ChoiceLoader(loaders),
            }

    if hasattr(settings, 'JINJA_CONFIG'):
        if hasattr(settings.JINJA_CONFIG, '__call__'):
            config = settings.JINJA_CONFIG()
        else:
            config = settings.JINJA_CONFIG
        opts.update(config)

    e = Environment(**opts)
    return e


def render(request, template, context=None, **kwargs):
    """
    Shortcut like Django's ``render_to_response``, but better.

    Minimal usage, with only a request object and a template name::

        return jingo.render(request, 'template.html')

    With template context and keywords passed to
    :class:`django.http.HttpResponse`::

        return jingo.render(request, 'template.html',
                            {'some_var': 42}, status=209)
    """
    rendered = render_to_string(request, template, context)
    return http.HttpResponse(rendered, **kwargs)


def render_to_string(request, template, context=None):
    """
    Render a template into a string.
    """
    def get_context():
        c = {} if context is None else context.copy()
        for processor in get_standard_processors():
            c.update(processor(request))
        return c

    # If it's not a Template, it must be a path to be loaded.
    if not isinstance(template, jinja2.environment.Template):
        template = env.get_template(template)

    return template.render(**get_context())


def load_helpers():
    """Try to import ``helpers.py`` from each app in INSTALLED_APPS."""
    # We want to wait as long as possible to load helpers so there aren't any
    # weird circular imports with jingo.
    global _helpers_loaded
    if _helpers_loaded:
        return
    _helpers_loaded = True

    from jingo import helpers

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('helpers', app_path)
        except ImportError:
            continue

        import_module('%s.helpers' % app)


class Register(object):
    """Decorators to add filters and functions to the template Environment."""

    def __init__(self, env):
        self.env = env

    def filter(self, f):
        """Adds the decorated function to Jinja's filter library."""
        self.env.filters[f.__name__] = f
        return f

    def function(self, f):
        """Adds the decorated function to Jinja's global namespace."""
        self.env.globals[f.__name__] = f
        return f

    def inclusion_tag(self, template):
        """Adds a function to Jinja, but like Django's @inclusion_tag."""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kw):
                context = f(*args, **kw)
                t = env.get_template(template).render(context)
                return jinja2.Markup(t)
            return self.function(wrapper)
        return decorator

env = get_env()
register = Register(env)


from jinja2 import utils


class _MarkupEscapeHelper(object):
    """
    A replacement for jinja's _MarkupEscapeHandler that doesn't use lambdas.
    Exceptions in the lambdas seem to cause the gc_refs crashes from
    bug 560381.
    """

    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        """
        We don't want localizers to take down the site when their string
        interpolation variables don't match the real strings.

        If we have {% trans users=... %}blah {{ users }}{% endtrans %}
        and the localizer has "blah %(user)s" in their gettext catalog, there will
        be a KeyError when Python looks for the users variable.
        """
        try:
            return self.obj[key]
        except KeyError:
            lang = trans_real.get_language()
            log.error(u'[%s] KeyError: %r in %r' % (lang, key, self.obj))

    def __str__(self):
        return str(utils.escape(self.obj))

    def __unicode__(self):
        return unicode(utils.escape(self.obj))

    def __repr__(self):
        return str(utils.escape(repr(self.obj)))

    def __int__(self):
        return int(self.obj)

    def __float__(self):
        return float(self.obj)


utils._MarkupEscapeHelper = _MarkupEscapeHelper
