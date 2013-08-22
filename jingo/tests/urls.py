from __future__ import unicode_literals

from django.conf.urls import patterns


urlpatterns = patterns('',
    (r'^url/(\d+)/(\w+)/$', lambda r: None, {}, "url-args"),
    (r'^url/(?P<num>\d+)/(?P<word>\w+)/$', lambda r: None, {}, "url-kwargs"),
)
