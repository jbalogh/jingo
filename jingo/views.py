import jingo


def direct_to_template(request, template, **kwargs):
    """
    Warning: This function is deprecated, rather use template loader
    jingo.Loader and django.shortcuts.render
    """
    return jingo.render(request, template, kwargs)
