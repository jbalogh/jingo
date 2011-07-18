.. _jingo:
.. module:: jingo

Jingo
=====


Jingo is an adapter for using
`Jinja2 <http://jinja.pocoo.org/2/documentation/>`_ templates within Django.
Why are we already replacing the templates?  AMO's current PHP templates let you
go hog-wild with logic in the templates, while Django is extremely restrictive.
Jinja loosens those restrictions somewhat, providing a more powerful engine with
the beauty of Django's templates.  The tipping point for me was the verbosity of
doing L10n in Django templates.


Settings
--------

If you want to configure the Jinja environment, use ``JINJA_CONFIG`` in
``settings.py``.  It can be a dict or a function that returns a dict. ::

    JINJA_CONFIG = {'autoescape': False}

or ::

    def JINJA_CONFIG():
        return {'the_answer': 41 + 1}

You'll want to use jingo's template loader::

    TEMPLATE_LOADERS = (
        'jingo.Loader',
    )

This will let you use ``django.shortcuts.render`` or
``django.shortcuts.render_to_response``.

Using the ``JINJA_TEMPLATE_SUBPATH`` setting, you can mix both Django and Jinja
templates in the same project::

    JINJA_TEMPLATE_SUBPATH = "/jinja"

    TEMPLATE_LOADERS = (
        'jingo.Loader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

When configured this way, the ``jingo.Loader`` will look for templates under a
``templates/jinja`` subdirectory both at the top-level and within each
installed app. If a particular template is not found there, the search will
fall back to Django template loaders.

This can be handy for using Jinja templates in your own apps while still
allowing the Django admin app and other third-party apps to function using
built-in templates as expected.

If ``JINJA_TEMPLATE_SUBPATH`` is left out of settings, the default value is
blank. This results in ``jingo.loader`` looking for templates in just the
``templates`` subdirectories. This can be useful for projects where Jinja is
expected to be the only templating system in use.
    

Template Helpers
----------------

Instead of template tags, Jinja encourages you to add functions and filters to
the templating environment.  In ``jingo``, we call these helpers.  When the
Jinja environment is initialized, ``jingo`` will try to open a ``helpers.py``
file from every app in ``INSTALLED_APPS``.  Two decorators are provided to ease
the environment extension:

.. function:: jingo.register.filter

    Adds the decorated function to Jinja's filter library.

.. function:: jingo.register.function

    Adds the decorated function to Jinja's global namespace.


.. highlight:: jinja

Default Helpers
~~~~~~~~~~~~~~~

Helpers are available in all templates automatically, without any extra
loading.

.. automodule:: jingo.helpers
    :members:


Template Environment
--------------------

A single Jinja ``Environment`` is created for use in all templates.  This is
available as ``jingo.env`` if you need to work with the ``Environment``.


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
