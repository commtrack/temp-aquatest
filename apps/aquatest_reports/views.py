from rapidsms.webui.utils import render_to_response, paginated
from xformmanager.models import *
from wqm.models import *
from hq.models import *
from graphing.models import *
from receiver.models import *
from domain.decorators import login_and_domain_required
from reporters.utils import *
from samples.models import *
from wqm.models import SamplingPoint
from reporters.models import Reporter
from samples.models import Parameter
import csv
from django.http import HttpResponse
#from django import http
#from django.shortcuts import render_to_response
#from django.template.loader import get_template
#from django.template import Context
#import ho.pisa as pisa
#import cStringIO as StringIO
#import cgi

logger_set = False

@login_and_domain_required
def reports(request):
    all_samples = Sample.objects.all()
    samples =[]
    for sample in all_samples:
        if sample.sampling_point.wqmarea not in samples:
            samples.append(sample.sampling_point.wqmarea)
    wqmarea = WqmArea.objects.all()
    template_name="reports.html"
    context = {}
    context = {
    "wqmarea":wqmarea,
    "samples":samples,
    "allwqmarea":wqmarea
    }


    return render_to_response(request, template_name,context)

@login_and_domain_required
def sampling_points(request):
    selected_points = request.POST.getlist('area')
    samplez = []
    sample_ids=[]
    all_samples = Sample.objects.filter(sampling_point__wqmarea__in= selected_points)
    for sample in all_samples:
        if sample.sampling_point not in samplez:
            samplez.append(sample.sampling_point)
    for sample_id in all_samples:
        sample_ids.append(sample_id.id)
    template_name="reports.html"
    context = {}
    context = {
    "sampling_points":sampling_points,
    "samples":samplez,
    "selected_wqmarea":sample_ids
    }


    return render_to_response(request, template_name,context)

@login_and_domain_required
def testers(request):
    selected_wqma = request.POST.getlist('selected_wqm')
    selected_samplingPoints = request.POST.getlist('sampling_points')
    samples = Sample.objects.filter(id__in = selected_wqma,
                                    sampling_point__in = selected_samplingPoints,
                                    )
    samples_ids=[]
    testers=[]
    for sample in samples:
        samples_ids.append(sample.id)
        if sample.taken_by not in testers:
            testers.append(sample.taken_by)
    template_name="reports.html"
    context = {}
    context = {
    "testers":testers,
    "selected_wqma":selected_wqma,
    "samples_ids":samples_ids,
    }


    return render_to_response(request, template_name,context)

def date_range(request):
    selected_testers = request.POST.getlist('testers')
    selected_wqm_samplingPoints = request.POST.getlist('selected_testers')
    samples = Sample.objects.filter(id__in = selected_wqm_samplingPoints,
                                    taken_by__in = selected_testers,
                                    
                                    )
    samples_ids=[]
    for sample in samples:
        samples_ids.append(sample.id)
    daterange = 1
    template_name="reports.html"
    context = {}
    context = {
    "daterange":daterange,
    "samples":samples,
    "samples_ids":samples_ids

    }


    return render_to_response(request, template_name,context)

def create_report(request):
    selected_wqm_samplingPoints_tester = request.POST.getlist('selected_all')
    selected_start_date = request.POST.getlist('startDate')
    datestart = []
    dateend =[]
    for p in selected_start_date:
        datestart.append(p)
    selected_end_date = request.POST.getlist('endDate')
    for j in selected_end_date:
        dateend.append(j)
    std = datetime(int(datestart[2]),int(datestart[1]),int(datestart[0]))
    ste = datetime(int(dateend[2]),int(dateend[1]),int(dateend[0]))
    samples = Sample.objects.filter(id__in = selected_wqm_samplingPoints_tester,
                                date_taken__range = (std,ste)
                                    )
    samples_ids=[]
    for sample in samples:
        samples_ids.append(sample.id)
    data = 1
    template_name="reports.html"

    context = {}
    context = {
        "data":data,
        "selected_start_date":std,
        "selected_end_date":ste,
        "samples_ids":samples_ids,
        "samples":samples
    }


    return render_to_response(request, template_name,context)

@login_and_domain_required
def data(request):
    selected_wqm_samplingPoints_tester = request.POST.getlist('selected_all')
    print '**********************'
    print selected_wqm_samplingPoints_tester
#    samples = Sample.objects.filter(id__in=selected_wqm_samplingPoints_tester)
    samples = Sample.objects.all()
    data = 1
    template_name="reports_samples.html"
    context = {}
    context = {
        "samples":samples,
        "data":data,
    }


    return render_to_response(request, template_name,context)

@login_and_domain_required
def points(request):

    template_name="reports_samples.html"
    context = {}
    context = {
        "samples":samples
    }


    return render_to_response(request, template_name,context)

@login_and_domain_required
#def export_csv(request):
#
#    template_name="reports_samples.html"
#    context = {}
#    response = HttpResponse(mimetype='text/csv')
#    response['Content-Disposition'] = 'attachment; filename=somefilename.csv'
#
#    writer = csv.writer(response)
#    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
#    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
#    context = {
#        "samples":samples
#    }
#
#
#    return render_to_response(request, template_name,context)

def export_csv(request):
    samples_to_export = request.POST.getlist('samples')
    print 'i am being executed====='

    samples = Sample.objects.filter(id__in = samples_to_export
                                    )
    for i in samples:
     print i.taken_by

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.csv'

    writer = csv.writer(response)
#    parms = Parameter.objects.all()
#    for parm in parms:
    writer.writerow(['Area', 'Sampling Point', 'Tester', 'Parameter','Parameter shortname'])
    for sample in samples:
        point = sample.sampling_point
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
            writer.writerow([point.wqmarea, point, sample.taken_by, result.value,result.parameter.test_name])
    return response

#def write_pdf(template_src="pdf.html", context_dict):
#    template = get_template(template_src)
#    context = Context(context_dict)
#    html  = template.render(context)
#    result = StringIO.StringIO()
#    pdf = pisa.pisaDocument(StringIO.StringIO(
#        html.encode("UTF-8")), result)
#    if not pdf.err:
#        return http.HttpResponse(result.getvalue(), \
#             mimetype='application/pdf')
#    return http.HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))
#
#def article(request):
#    article = get_object_or_404(Article, pk=id)
#
#    return write_pdf('dtd/pdf/template.html',{
#        'pagesize' : 'A4',
#        'article' : article})


######################
#def indexi(request):
#    return http.HttpResponse("""
#        <html><body>
#            <h1>Example 1</h1>
#            Please enter some HTML code:
#            <form action="/download/" method="post" enctype="multipart/form-data">
#            <textarea name="data">Hello <strong>World</strong></textarea>
#            <br />
#            <input type="submit" value="Convert HTML to PDF" />
#            </form>
#            <hr>
#            <h1>Example 2</h1>
#            <p><a href="ezpdf_sample">Example with template</a>
#        </body></html>
#        """)
#
#def download(request):
#    if request.POST:
#        result = StringIO.StringIO()
#        pdf = pisa.CreatePDF(
#            StringIO.StringIO(request.POST["data"]),
#            result
#            )
#
#        if not pdf.err:
#            return http.HttpResponse(
#                result.getvalue(),
#                mimetype='application/pdf')
#
#    return http.HttpResponse('We had some errors')
#
#def render_to_pdf(template_src, context_dict):
#    template = get_template(template_src)
#    context = Context(context_dict)
#    html  = template.render(context)
#    result = StringIO.StringIO()
#    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
#    if not pdf.err:
#        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
#    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
#
#def ezpdf_sample(request):
#    blog_entries = []
#    for i in range(1,10):
#        blog_entries.append({
#            'id': i,
#            'title':'Playing with pisa 3.0.16 and dJango Template Engine',
#            'body':'This is a simple example..'
#            })
#    return render_to_pdf('entries.html',{
#        'pagesize':'A4',
#        'title':'My amazing blog',
#        'blog_entries':blog_entries})