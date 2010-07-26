from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^calenderjs$', 'calender.views.cal'),
#    (r'^calenderjs$', 'calender.views.callenderdata'),
#    (r'^calenderjs$', 'calender.views.getsamplebydate'),
#    (r'^calenderjs$', 'calender.views.countdaysamples'),

)

