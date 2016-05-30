.. _jingo:
.. module:: jingo

=====
Jingo
=====

.. note:: This document may be out of date.  The up-to-date documentation can
   be found on `Read the Docs <https://jingo.readthedocs.org/en/latest/>`_.


Jingo is an adapter for using Jinja2_ templates within Django.


Jingo is DEPRECATED
-------------------

In version 1.8, Django added support for multiple template engines, and provided
a Jinja2 backend.  The django-jinja_ project leverages that to support Jinja2,
while Jingo does not.

**django-jinja is recommended for new projects.** Jingo >=0.8 supports Django
1.8, but it will not be maintained beyond version 0.9, and **will not** support
Django 1.9 or above.  If you're already using Jingo, and not ready to make `the
switch`_, Jingo should continue to work for now, though not without some effort.

0.9_ will be the last release of Jingo, unless a new maintainer comes along with
a new direction.

As of 0.9, Jingo's built-in helpers are provided via a `Jinja2 extension`_ to
simplify moving away from Jingo. The entire ``jingo/ext.py`` file can be copied
into another project, or referenced as ``'jingo.ext.JingoExtension'``. Used in
this way, Jingo plays nicely with django-jinja (and theoretically Django's
built-in Jinja2 backend).

.. _django-jinja: https://github.com/niwinz/django-jinja
.. _the switch: http://bluesock.org/~willkg/blog/mozilla/input_django_1_8_upgrade.html#switching-from-jingo-to-django-jinja
.. _Jinja2: http://jinja.pocoo.org/2/
.. _0.9: https://https://pypi.python.org/pypi/jingo/0.9.0
.. _Jinja2 extension: https://github.com/jbalogh/jingo/blob/master/jingo/ext.py


.. _usage:

Usage
-----

When configured properly (see Settings_ below) you can render Jinja2_ templates in
your view the same way you'd render Django templates::

    from django.shortcuts import render


    def my_view(request):
        context = dict(user_ids=(1, 2, 3, 4))
        return render(request, 'users/search.html', context)

.. note::

    Not only does ``django.shorcuts.render`` work, but so does any method that
    Django provides to render templates.

.. _settings:

Settings
--------

You'll want to use Django to use jingo's template loader.
In ``settings.py``::

    TEMPLATE_LOADERS = (
        'jingo.Loader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

This will let you use ``django.shortcuts.render`` or
``django.shortcuts.render_to_response``.

You can optionally specify which filename patterns to consider Jinja2 templates::

    JINGO_INCLUDE_PATTERN = r'\.jinja2'  # use any regular expression here

This will consider every template file that contains the substring `.jinja2` to
be a Jinja2 file (unless it's in a module explicitly excluded, see below).

And finally you may have apps that do not use Jinja2, these must be excluded
from the loader::

    JINGO_EXCLUDE_APPS = ('debug_toolbar',)

If a template path begins with ``debug_toolbar``, the Jinja loader will raise a
``TemplateDoesNotExist`` exception. This causes Django to move onto the next
loader in ``TEMPLATE_LOADERS`` to find a template - in this case,
``django.template.loaders.filesystem.Loader``.

.. note::
   Technically, we're looking at the template path, not the app. Often these are
   the same, but in some cases, like 'registration' in the default setting--which
   is an admin template--they are not.

The default is in ``jingo.EXCLUDE_APPS``::

    EXCLUDE_APPS = (
        'admin',
        'admindocs',
        'registration',
        'context_processors',
    )

.. versionchanged:: 0.6.2
   Added ``context_processors`` application.

If you want to configure the Jinja environment, use ``JINJA_CONFIG`` in
``settings.py``.  It can be a dict or a function that returns a dict. ::

    JINJA_CONFIG = {'autoescape': False}

or::

    def JINJA_CONFIG():
        return {'the_answer': 41 + 1}

If you set the ``extensions`` key in the configuration, you **must**
include ``jingo.ext.JingoExtension`` to get Jingo's built-in template
helpers (see below).


Template Helpers
----------------

.. note::

    In the interest of future-proofing, consider writing custom filters and
    functions as Jinja extensions. See ``jingo/ext.py`` for a simple example.

Instead of template tags, Jinja encourages you to add functions and filters to
the templating environment.  In ``jingo``, we call these helpers.  When the
Jinja environment is initialized, ``jingo`` will try to open a ``helpers.py``
file from every app in ``INSTALLED_APPS``.  Two decorators are provided to ease
the environment extension:

.. function:: jingo.register.filter

    Adds the decorated function to Jinja's filter library.

.. function:: jingo.register.function

    Adds the decorated function to Jinja's global namespace.


Default Helpers
~~~~~~~~~~~~~~~

Helpers are available in all templates automatically, without any extra
loading. See ``jingo/ext.py`` for their definitions.


Template Environment
--------------------

A single Jinja ``Environment`` is created for use in all templates.  This is
available via ``jingo.get_env()`` if you need to work with the ``Environment``.


Localization
------------

Since we all love L10n, let's see what it looks like in Jinja templates::

    <h2>{{ _('Reviews for {0}')|f(addon.name) }}</h2>

The simple way is to use the familiar underscore and string within a ``{{ }}``
moustache block.  ``f`` is an interpolation filter documented below.  Sphinx
could create a link if I knew how to do that.

The other method uses Jinja's ``trans`` tag::

    {% trans user=review.user|user_link, date=review.created|datetime %}
        by {{ user }} on {{ date }}
    {% endtrans %}

``trans`` is nice when you have a lot of text or want to inject some variables
directly.  Both methods are useful, pick the one that makes you happy.


Forms
-----

Django marks its form HTML "safe" according to its own rules, which Jinja2 does
not recognize.

This monkeypatches Django to support the ``__html__`` protocol used in Jinja2
templates. ``Form``, ``BoundField``, ``ErrorList``, and other form objects that
render HTML through their ``__unicode__`` method are extended with ``__html__``
so they can be rendered in Jinja2 templates without adding ``|safe``.

Call the ``patch()`` function to execute the patch. It must be called
before ``django.forms`` is imported for the conditional_escape patch to work
properly. The root URLconf is the recommended location for calling ``patch()``.

Usage::

    import jingo.monkey
    jingo.monkey.patch()


Testing
-------

To run the test suite, you need to define ``DJANGO_SETTINGS_MODULE`` first::

    $ export DJANGO_SETTINGS_MODULE="fake_settings"
    $ nosetests

or simply run::

    $ python run_tests.py

To test on all supported versions of Python and Django::

    $ pip install tox
    $ tox
