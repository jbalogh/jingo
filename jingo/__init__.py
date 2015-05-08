"""Adapter for using Jinja2 with Django."""

from __future__ import unicode_literals

import functools
import imp
import logging
import re

from django.conf import settings
from django.template.base import Origin, TemplateDoesNotExist
from django.template.context import get_standard_processors
from django.template.loader import BaseLoader
from django.utils.importlib import import_module

import jinja2

VERSION = (0, 7, 0)
__version__ = '.'.join(map(str, VERSION))

EXCLUDE_APPS = (
    'admin',
    'admindocs',
    'registration',
    'context_processors',
)

log = logging.getLogger('jingo')


class Environment(jinja2.Environment):
    _helpers_loaded = False

    def get_template(self, name, parent=None, globals=None):
        """Make sure our helpers get loaded before any templates."""
        self._load_helpers()
        return super(Environment, self).get_template(name, parent, globals)

    def from_string(self, source, globals=None, template_class=None):
        self._load_helpers()
        return super(Environment, self).from_string(source, globals,
                                                    template_class)

    def _load_helpers(self):
        """Try to import ``helpers.py`` from each app in INSTALLED_APPS."""
        # We want to wait as long as possible to load helpers so there aren't any
        # weird circular imports with jingo.
        if self._helpers_loaded:
            return
        self._helpers_loaded = True

        from jingo import helpers  # noqa

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
    # Install null translations since gettext isn't always loaded up during
    # testing.
    if ('jinja2.ext.i18n' in e.extensions or
            'jinja2.ext.InternationalizationExtension' in e.extensions):
        e.install_null_translations()
    return e


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

    return template.render(get_context())


class Register(object):
    """Decorators to add filters and functions to the template Environment."""

    def __init__(self, env):
        self.env = env

    def filter(self, f=None, override=True):
        """Adds the decorated function to Jinja's filter library."""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kw):
                return f(*args, **kw)
            return self.filter(wrapper, override)

        if not f:
            return decorator
        if override or f.__name__ not in self.env.filters:
            self.env.filters[f.__name__] = f
        return f

    def function(self, f=None, override=True):
        """Adds the decorated function to Jinja's global namespace."""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kw):
                return f(*args, **kw)
            return self.function(wrapper, override)

        if not f:
            return decorator
        if override or f.__name__ not in self.env.globals:
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


class Template(jinja2.Template):

    def render(self, context={}):
        """Render's a template, context can be a Django Context or a
        dictionary.
        """
        # flatten the Django Context into a single dictionary.
        context_dict = {}
        if hasattr(context, 'dicts'):
            for d in context.dicts:
                context_dict.update(d)
        else:
            context_dict = context

            # Django Debug Toolbar needs a RequestContext-like object in order
            # to inspect context.
            class FakeRequestContext:
                dicts = [context]
            context = FakeRequestContext()

        # Used by debug_toolbar.
        if settings.TEMPLATE_DEBUG:
            from django.test import signals
            self.origin = Origin(self.filename)
            signals.template_rendered.send(sender=self, template=self,
                                           context=context)

        return super(Template, self).render(context_dict)


class Loader(BaseLoader):
    is_usable = True
    env.template_class = Template

    def __init__(self):
        super(Loader, self).__init__()
        include_pattern = getattr(settings, 'JINGO_INCLUDE_PATTERN', None)
        if include_pattern:
            self.include_re = re.compile(include_pattern)
        else:
            self.include_re = None

    def _valid_template(self, template_name):
        if self.include_re:
            if not self.include_re.search(template_name):
                return False

        if hasattr(template_name, 'split'):
            app = template_name.split('/')[0]
            if app in getattr(settings, 'JINGO_EXCLUDE_APPS', EXCLUDE_APPS):
                return False

        return True

    def load_template(self, template_name, template_dirs=None):
        if not self._valid_template(template_name):
            raise TemplateDoesNotExist(template_name)

        try:
            template = env.get_template(template_name)
            return template, template.filename
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)

    def load_template_source(self, template_name, template_dirs=None):
        if not self._valid_template(template_name):
            raise TemplateDoesNotExist(template_name)

        try:
            template = env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)

        with open(template.filename, 'rb') as fp:
            return (fp.read().decode(settings.FILE_CHARSET), template.filename)
