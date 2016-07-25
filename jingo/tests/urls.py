from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
    url(r'^url/(\d+)/(\w+)/$', lambda r: None, {}, "url-args"),
    url(r'^url/(?P<num>\d+)/(?P<word>\w+)/$', lambda r: None, {}, "url-kwargs"),
]
