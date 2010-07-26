from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^samplingpoints$', 'wqm.views.index'),
    (r'^samplingpoints/add$', 'wqm.views.add_samplingpoint'),
    (r'^samplingpoints/(?P<pk>\d+)$', 'wqm.views.edit_samplingpoints'),
    (r'^samplingpoints/(?P<pk>\d+)/delete$', 'wqm.views.delete_samplingpoints'),
)