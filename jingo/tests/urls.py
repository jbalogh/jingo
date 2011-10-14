from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^url/(\d+)/(\w+)/$', lambda r: None, {}, "url-args"),
    (r'^url/(?P<num>\d+)/(?P<word>\w+)/$', lambda r: None, {}, "url-kwargs"),
)
