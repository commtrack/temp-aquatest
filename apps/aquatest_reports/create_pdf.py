from xformmanager.models import *
from wqm.models import *
from hq.models import *
from graphing.models import *
from receiver.models import *
from reporters.utils import *
from samples.models import *
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from samples.models import *
from wqm.models import *

styleSheet = getSampleStyleSheet()

def run(response,request,selected_parameters):
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
    doc = SimpleDocTemplate(response, pagesize=(8.5*inch, 11*inch),)
    lst = []


    styNormal = styleSheet['Normal']
    styBackground = ParagraphStyle('background', parent=styNormal)
    styH1 = styleSheet['title']
    month_names = ['0','jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    head = "AquaTest Report"
    head2 = "Date Range : %s-%s-%s to %s-%s-%s" % (styear,month_names[stmonth],stday,endyear,month_names[endmonth],endday)
    lst.append(Paragraph(head, styH1))
    lst.append(Paragraph(' ', styH1))
    lst.append(Paragraph(head2, styNormal))
    lst.append(Paragraph(' ', styH1))

    ts1 = TableStyle([
                ('ALIGN', (0,0), (-1,0), 'RIGHT'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                    ])
    pdf = []
    title = [Paragraph('Date Taken', styBackground),Paragraph('Area', styBackground), Paragraph('Sampling Point', styBackground), Paragraph('Tester', styBackground)]
    params = []
    for para in selected_parameters:
        title.append(Paragraph(para, styBackground))
        params.append(para)
    pdf.append(title)
    for sample in samples:
        Data = []
        point = sample.sampling_point
        results = MeasuredValue.objects.filter(sample=sample,parameter__test_name__in = selected_parameters)

        dayData = []
        if results:
            for result in results:
                if result.sample.id not in dayData:
                    dayData.append(result.sample.id)
                dayData.append(result.parameter.test_name)
                dayData.append(result.value)
            date = '%s-%s-%s'%(sample.date_taken.year,month_names[sample.date_taken.month],sample.date_taken.day)
            ares = '%s'%point.wqmarea
            smpling = '%s'%point
            testr = '%s'% sample.taken_by
            data = [Paragraph( date, styBackground), Paragraph(ares, styBackground),Paragraph(smpling , styBackground),Paragraph(testr, styBackground)]
            pdf.append(data)
            Data.append(dayData)
            for i,li in enumerate(Data):
                for titl in params:
                    if li[0]==result.sample.id:
                        if titl in li:
                            val = int(li.index(titl))
                            val = val + 1
                            data.append(Paragraph((Data[i][val]), styBackground))
                        else:
                            data.append(Paragraph('-', styBackground))
    t1 = Table(
    pdf
        )
    t1.setStyle(ts1)
    lst.append(t1)
    lst.append(Spacer(0,10))

    doc.build(lst)

