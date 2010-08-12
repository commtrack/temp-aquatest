from django.conf.urls.defaults import *

## reports view
urlpatterns = patterns('aquatest_reports.views',
    (r'^reports$', 'reports'),
    (r'^sampling_points$', 'sampling_points'),
    (r'^report_testers$', 'testers'),
    (r'^date_range$', 'date_range'),
    (r'^create_report$', 'create_report'),
    (r'^export_csv$', 'export_csv'),
    (r'^export_pdf$', 'pdf_view'),
    (r'^parameters$', 'parameters'),

)


