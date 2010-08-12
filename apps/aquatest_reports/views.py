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
import create_pdf
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()
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

@login_and_domain_required
def parameters(request):
    selected_testers = request.POST.getlist('testers')
    selected_wqm_samplingPoints = request.POST.getlist('selected_testers')
    samples = Sample.objects.filter(id__in = selected_wqm_samplingPoints,
                                    taken_by__in = selected_testers,

                                    )
    samples_ids=[]
    parameter=[]
    for sample in samples:
        samples_ids.append(sample.id)
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
                if result.parameter.test_name not in parameter:
                    parameter.append(result.parameter.test_name)
    template_name="reports.html"
    context = {}
    context = {
    "parameter":parameter,
    "selected_wqma":selected_testers,
    "samples_ids":samples_ids,
    }


    return render_to_response(request, template_name,context)

def date_range(request):
    selected_params = request.POST.getlist('parameter')

    selected_wqm_samplingPoints_params = request.POST.getlist('selected_parameter')
    samples = Sample.objects.filter(id__in = selected_wqm_samplingPoints_params,
                                    )
    samples_ids=[]
    for sample in samples:
            samples_ids.append(sample.id)
    daterange = 1
    end_date = datetime.today()
    month_names = ['0','jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    start_date = datetime(end_date.year-1,end_date.month,end_date.day)
    month_name = month_names[end_date.month]
    template_name="reports.html"
    context = {}
    context = {
    "daterange":daterange,
    "samples":samples,
    "samples_ids":samples_ids,
    "start_date":start_date,
    "end_date":end_date,
    "month_names":month_name,
    "selected_params":selected_params,

    }


    return render_to_response(request, template_name,context)

def create_report(request):
    selected_parameters = request.POST.getlist('selected_params')
    #clean parameters data
    del selected_parameters[len(selected_parameters)-1]
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
        "samples":samples,
        "selected_params":selected_parameters
    }


    return render_to_response(request, template_name,context)


@login_and_domain_required
def export_csv(request):
    selected_param = request.POST.getlist('selected_params')
    samples_to_export = request.POST.getlist('samples')

    samples = Sample.objects.filter(id__in = samples_to_export
                                    )

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.csv'

    writer = csv.writer(response)
    month_names = ['0','jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    title = ['Date taken','Area', 'Sampling Point', 'Tester']
    params = selected_param
    for para in selected_param:
        title.append(para)
    writer.writerow(title)

    for sample in samples:
        Data = []
        point = sample.sampling_point
        results = MeasuredValue.objects.filter(sample=sample, parameter__test_name__in = selected_param)
        if results:
            dayData = []
            month_name = month_names[sample.date_taken.month]
            date = '%s-%s-%s'%(sample.date_taken.year,month_name,sample.date_taken.day)
            data = [date ,point.wqmarea, point, sample.taken_by]
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
                            data.append('-')
            writer.writerow(data)
    return response

@login_and_domain_required
def pdf_view(request):
    selected_parameters = request.POST.getlist('selected_params')
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=AquaTestReport.pdf'
    create_pdf.run(response, request,selected_parameters)
    return response

