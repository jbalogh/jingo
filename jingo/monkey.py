"""
This monkeypatches Django to support the __html__ protocol used in Jinja
templates. Form, BoundField, ErrorList, and other form objects that
render HTML through their __unicode__ method are extended with __html__
so they can be rendered in Jinja templates without adding |safe.

Call the patch() function to execute the patch. It must be called
before django.forms is imported for the conditional_escape patch to work
properly. The root URLconf is the recommended location for calling patch().

Usage::

    import jingo.monkey
    jingo.monkey.patch()

This patch was originally developed by Jeff Balogh and this version is taken
from the nuggets project at
https://github.com/mozilla/nuggets/blob/master/safe_django_forms.py

"""
import django.utils.encoding
import django.utils.html
import django.utils.safestring


# This function gets directly imported within Django, so this change needs to
# happen before too many Django imports happen.
def conditional_escape(html):
    """
    Similar to escape(), except that it doesn't operate on pre-escaped strings.
    """
    if hasattr(html, '__html__'):
        return html.__html__()
    elif isinstance(html, django.utils.safestring.SafeData):
        return html
    return django.utils.html.escape(html)


# Django uses SafeData to mark a string that has already been escaped or
# otherwise deemed safe. This __html__ method lets Jinja know about that too.
def __html__(self):
    """
    Returns the html representation of a string.

    Allows interoperability with other template engines.
    """
    return unicode(self)


# Django uses StrAndUnicode for classes like Form, BoundField, Widget which
# have a __unicode__ method which returns escaped html. We replace
# StrAndUnicode with SafeStrAndUnicode to get the __html__ method.
class SafeStrAndUnicode(django.utils.encoding.StrAndUnicode):
    """A class whose __str__ and __html__ returns __unicode__."""

    def __html__(self):
        return unicode(self)


def patch():
    django.utils.html.conditional_escape = conditional_escape
    django.utils.safestring.SafeData.__html__ = __html__

    # forms imports have to come after we patch conditional_escape.
    from django.forms import forms, formsets, util, widgets

    # Replace StrAndUnicode with SafeStrAndUnicode in the inheritance
    # for all these classes.
    classes = (
        forms.BaseForm,
        forms.BoundField,
        formsets.BaseFormSet,
        util.ErrorDict,
        util.ErrorList,
        widgets.Media,
        widgets.RadioInput,
        widgets.RadioFieldRenderer,
    )

    for cls in classes:
        bases = list(cls.__bases__)
        if django.utils.encoding.StrAndUnicode in bases:
            idx = bases.index(django.utils.encoding.StrAndUnicode)
            bases[idx] = SafeStrAndUnicode
            cls.__bases__ = tuple(bases)
    for cls in classes:
        if not hasattr(cls, '__html__'):
            cls.__html__ = __html__
