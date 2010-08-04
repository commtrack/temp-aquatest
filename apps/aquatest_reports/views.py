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

from reportlab.pdfgen import canvas
#from reportlab import *

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
def export_csv(request):
    samples_to_export = request.POST.getlist('samples')

    samples = Sample.objects.filter(id__in = samples_to_export
                                    )

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.csv'

    writer = csv.writer(response)

    title = ['Area', 'Sampling Point', 'Tester']
    params = []
    for sample in samples:
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
                if result.parameter.test_name not in title:
                    title.append(result.parameter.test_name)
                    params.append(result.parameter.test_name)
    writer.writerow(title)

    for sample in samples:
        Data = []
        point = sample.sampling_point
        results = MeasuredValue.objects.filter(sample=sample)
        dayData = []
        data = [point.wqmarea, point, sample.taken_by]
        for result in results:
            if result.sample.id not in dayData:
                dayData.append(result.sample.id)
            dayData.append(result.parameter.test_name)
            dayData.append(result.value)
        Data.append(dayData)
        for i,li in enumerate(Data):
            for titl in params:
                if li[0]==result.sample.id:
                    if titl in li:
                        val = int(li.index(titl))
                        val = val + 1
                        data.append((Data[i][val]))
                    else:
                        data.append('')
        writer.writerow(data)
    return response

@login_and_domain_required
def pdf_view(request):
    samples_to_export = request.POST.getlist('samples')
    samples = Sample.objects.filter(id__in = samples_to_export
                                    )
    std = request.POST.get('start_date').split('-')
    ste = request.POST.get('end_date').split('-')
    styear = int(std[0])
    stmonth = int(std[1])
    stday = int(std[2])
    endyear = int(ste[0])
    endmonth = int(ste[1])
    endday = int(ste[2])
    samples
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
#    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.pdf'
    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.pdf'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)
    title = "AquaTest Report for date Range %s-%s-%s to %s-%s-%s" % (styear,stmonth,stday,endyear,endmonth,endday)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    title2 = []

    for sample in samples:
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
                if result.parameter.test_name not in title2:
                    title2.append(result.parameter.test_name)

    p.drawString(100,750, title)

    i = 50
    j = 700
    p.drawString(i,j, "Area")
    i = i + 50
    p.drawString(i,j, "Sampling Point")
    i = i + 100
    p.drawString(i,j, "Tester")
    i = i + 100
    for titles in title2:
        desplay = ' %s '% titles
        p.drawString(i,j, desplay)
        i = i + 80
    j = j - 50
    for sample in samples:
        i = 50
        point = sample.sampling_point
        area = "%s" % point.wqmarea
        sampling = "%s" % point
        tester = "%s" % sample.taken_by
        p.drawString(i,j, area)
        i = i + 50
        p.drawString(i,j, sampling)
        i = i + 100
        p.drawString(i,j, tester)
        i = i + 100
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
            data = "%s" % result.value
            p.drawString(i,j, data)
            i = i + 80
        j = j - 15

#    p.drawString(Paragraph("Wumpus vs Cave Population Report",
# styles['Title']))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response