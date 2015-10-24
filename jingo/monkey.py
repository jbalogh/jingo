"""
Django marks its form HTML "safe" according to its own rules, which Jinja2 does
not recognize.

This monkeypatches Django's Form classes to support __html__, which both Django
and Jinja2 use to identify already-vetted markup.

Call the ``patch()`` function to execute the patch. It must be called
before ``django.forms`` is imported for the conditional_escape patch to work
properly. The root URLconf is the recommended location for calling ``patch()``.

Usage::

    import jingo.monkey
    jingo.monkey.patch()

This patch was originally developed by Jeff Balogh.

"""

from __future__ import absolute_import, print_function, unicode_literals

from django.utils import six


def __html__(self):
    return six.text_type(self)


def patch():
    from django.forms import forms, formsets, util, widgets

    # Add __html__ methods to these classes:
    classes = [
        forms.BaseForm,
        forms.BoundField,
        formsets.BaseFormSet,
        util.ErrorDict,
        util.ErrorList,
        widgets.Media,
        widgets.RadioFieldRenderer,
    ]
    try:
        classes.append(widgets.RadioChoiceInput)
    except AttributeError:
        classes.append(widgets.RadioInput)

    for cls in classes:
        if not hasattr(cls, '__html__'):
            cls.__html__ = __html__
