"""
Extension of DjangoTestSuiteRunner without it, isn`t possible test views working with jinja2 templates, because Django
Client response.templates and response.context isn`t set.
JingoTestSuiteRunner provides testing utilities via standart django methods:
    def testView(self):
        client = Client()
        response = client.get('/my_url')
        self.assertEqual(response.context['var1'], 'value')
        self.assertFormError(response, 'form', 'login', 'Form error message')
        self.assertTemplateUsed(response, 'accounts/registration.htm')

In settings.py file please set TEST_RUNNER = 'jingo.utils.JingoTestSuiteRunner'

Thank Evgeny for inspiration
http://stackoverflow.com/questions/1941980/how-can-i-access-response-context-when-testing-a-jinja2-powered-django-view
"""

from django.template.response import TemplateResponse

from django.test.simple import DjangoTestSuiteRunner
from jinja2 import Template as Jinja2Template
from django.test import signals

def jinja2_instrumented_render(template, *args, **kwargs):
    context = dict(*args, **kwargs)
    signals.template_rendered.send(sender=template, template=template, context=context)
    return Jinja2Template.original_render(template, *args, **kwargs)

class JingoTestSuiteRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        super(JingoTestSuiteRunner, self).setup_test_environment(**kwargs)

        Jinja2Template.original_render = Jinja2Template.render
        Jinja2Template.render = jinja2_instrumented_render

    def teardown_test_environment(self, **kwargs):
        super(JingoTestSuiteRunner, self).teardown_test_environment(**kwargs)

        Jinja2Template.render = Jinja2Template.original_render
        del Jinja2Template.original_render
