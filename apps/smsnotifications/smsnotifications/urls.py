from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^smsnotification$', 'smsnotifications.views.index'),
    (r'^smsnotification/add$', 'smsnotifications.views.add_notifications'),
    (r'^smsnotification/(?P<pk>\d+)$', 'smsnotifications.views.edit_notifications'),
    (r'^smsnotification/(?P<pk>\d+)/delete$', 'smsnotifications.views.delete_notifications'),
)