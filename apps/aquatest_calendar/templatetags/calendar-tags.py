from django import template
from xformmanager.models import *
from hq.models import *
from hq.models import *
register = template.Library()
from samples.models import *
from wqm.models import *

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'

def _get_class(count):
    if count % 2 == 0:
        return "even"
    return "odd"

def _getsamples(day,month,year,area):
    check = int(area)
    if check == 0:
        samples = Sample.objects.filter(date_taken__day = day,
                                    date_taken__month = month,
                                    date_taken__year = year)
    else:
        a = Sample.objects.filter(date_taken__day = day,
                                    date_taken__month = month,
                                    date_taken__year = year)
        samples = a.filter(sampling_point__wqmarea = area)
    return samples


@register.simple_tag
def get_samples(day,month,year,area):
    samples = _getsamples(day,month,year,area)

    ret = ''
    ret += '''<table>\n<thead><tr>
            <th>Sampling point (Area)</th>
            <th>Taken by</th>
            <th>Date Taken</th>
            <th>Date Received</th>
            <th>Results</th></tr></thead>'''
    count = 1
    if samples:
        for sample in samples:
                ret += '\n<tr class="%s">' % _get_class(count)
                count += 1
                point = sample.sampling_point
                ret += '<td>%s (%s)</td>' % (point, point.wqmarea)
                ret += '<td>%s</td>' % (sample.taken_by)
                ret += '<td>%s-%s-%s</td>' % (sample.date_taken.day,sample.date_taken.month,sample.date_taken.year)
                ret += '<td>%s-%s-%s</td>' % (sample.date_taken.day,sample.date_taken.month,sample.date_taken.year)
                results = MeasuredValue.objects.filter(sample=sample)
                if results:
                    ret += '<td>'
                    for result in results:
                        ret += '%s-%s, ' % (result.value, result.parameter.test_name_short)
                    ret += '</td>'
                else:
                    ret += '<td>%s</td>' % ('No parameter for this submited sample')
                ret += '</tr>'
    else:
        ret += '<td>No samples submitted</td>'
    ret += '</tbody></table>'
    return ret
