"""Adapter for using Jinja2 with Django."""

from __future__ import unicode_literals

import functools
import logging
import re

from django.apps import apps
from django.conf import settings
from django.template.base import Origin, TemplateDoesNotExist
from django.template.loader import BaseLoader

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    import importlib.util
    if hasattr(importlib.util, 'find_spec'):  # Py3>=3.4
        def has_helpers(config):
            module = '%s.helpers' % (config.name,)
            return importlib.util.find_spec(module) is not None
    else:  # Py3<3.4
        def has_helpers(config):
            # For Python 3.3, just try to import the module. Unfortunately,
            # this changes the contract slightly for Python 3.3: if there is an
            # module but this raises a legitimate ImportError, jingo will act
            # as if the module doesn't exist. The intent is that we raise
            # legitimate ImportErrors but ignore missing modules.
            try:
                import_module('%s.helpers' % config.name)
                return True
            except ImportError:
                return False
except ImportError:
    import imp

    def has_helpers(config):
        try:
            imp.find_module('helpers', [config.path])
            return True
        except ImportError:
            return False

import jinja2

try:
    from django.template.engine import Engine

    has_engine = True

    def get_standard_processors():
        return Engine.get_default().template_context_processors

except ImportError:
    from django.template.context import get_standard_processors
    has_engine = False

VERSION = (0, 9, 0)
__version__ = '.'.join(map(str, VERSION))

EXCLUDE_APPS = (
    'admin',
    'admindocs',
    'registration',
    'context_processors',
)

log = logging.getLogger('jingo')

_helpers_loaded = False


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


class Environment(jinja2.Environment):
    template_class = Template

    def get_template(self, name, parent=None, globals=None):
        """Make sure our helpers get loaded before any templates."""
        load_helpers()
        return super(Environment, self).get_template(name, parent, globals)

    def from_string(self, source, globals=None, template_class=None):
        load_helpers()
        return super(Environment, self).from_string(source, globals,
                                                    template_class)


_env = None


def get_env():
    """Configure and return a jinja2 Environment."""
    global _env
    if _env:
        return _env
    # Mimic Django's setup by loading templates from directories in
    # TEMPLATE_DIRS and packages in INSTALLED_APPS.
    loaders = [jinja2.FileSystemLoader(d) for d in settings.TEMPLATE_DIRS]
    loaders += [jinja2.PackageLoader(c.name) for c in apps.get_app_configs()]

    opts = {
        'trim_blocks': True,
        'extensions': ['jinja2.ext.i18n', 'jingo.ext.JingoExtension'],
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
    _env = e
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
        template = get_env().get_template(template)

    return template.render(get_context())


def load_helpers():
    """Try to import ``helpers.py`` from each app in INSTALLED_APPS."""
    # We want to wait as long as possible to load helpers so there aren't any
    # weird circular imports with jingo.
    global _helpers_loaded
    if _helpers_loaded:
        return
    _helpers_loaded = True

    for config in apps.get_app_configs():
        if not has_helpers(config):
            continue

        import_module('%s.helpers' % config.name)


class Register(object):
    """Decorators to add filters and functions to the template Environment."""
    def filter(self, f=None, override=True):
        """Adds the decorated function to Jinja's filter library."""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kw):
                return f(*args, **kw)
            return self.filter(wrapper, override)

        if not f:
            return decorator
        if override or f.__name__ not in get_env().filters:
            get_env().filters[f.__name__] = f
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
        if override or f.__name__ not in get_env().globals:
            get_env().globals[f.__name__] = f
        return f

    def inclusion_tag(self, template):
        """Adds a function to Jinja, but like Django's @inclusion_tag."""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kw):
                context = f(*args, **kw)
                t = get_env().get_template(template).render(context)
                return jinja2.Markup(t)
            return self.function(wrapper)
        return decorator

register = Register()


class Loader(BaseLoader):
    is_usable = True

    def __init__(self):
        if has_engine:
            super(Loader, self).__init__(Engine.get_default())
        else:
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
            template = get_env().get_template(template_name)
            return template, template.filename
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)

    def load_template_source(self, template_name, template_dirs=None):
        if not self._valid_template(template_name):
            raise TemplateDoesNotExist(template_name)

        try:
            template = get_env().get_template(template_name)
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)

        with open(template.filename, 'rb') as fp:
            return (fp.read().decode(settings.FILE_CHARSET), template.filename)
