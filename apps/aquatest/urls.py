from django.conf.urls.defaults import *
import aquatest.views as views

urlpatterns = patterns('',
    (r'^testers$', 'aquatest.views.index'),
    (r'^testers/add$', 'aquatest.views.add_testers'),
    (r'^testers/(?P<pk>\d+)$', 'aquatest.views.edit_testers'),
    (r'^testers/(?P<pk>\d+)/delete$', 'aquatest.views.delete_testers'),
)