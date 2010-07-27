from django.conf.urls.defaults import *

## calendar view
urlpatterns = patterns('aquatest_calendar.views',
    (r'^calender$', 'view'),
    (r'^samplepop/$', 'samples_pop'),

)


