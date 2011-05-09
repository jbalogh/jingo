from django.views.generic import base
import jingo


def direct_to_template(request, template, **kwargs):
    return jingo.render(request, template, kwargs)


class JingoResponseMixin(base.TemplateResponseMixin):
    template_name = None
    response_class = jingo.TemplateResponse
