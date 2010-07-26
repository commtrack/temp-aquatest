from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^aquareports11$', 'aquaReports.views.index'),
    (r'^aquareports$', 'aquaReports.views.samplesreport'),
    (r'^parameterreport$', 'aquaReports.views.samplesreport'),
    (r'^samplereport$', 'aquaReports.views.samplesreport'),
    (r'^pdfview','aquaReports.views.pdf_view'),
    (r'^report_testers','aquaReports.views.report_testers'),
)


