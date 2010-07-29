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

#def _getsamples()
#    samples = Sample.objects.all()
#    return samples


@register.simple_tag
def get_samples(samples):
#    samples = Sample.objects.all()
    title = []
    for sample in samples:
        results = MeasuredValue.objects.filter(sample=sample)
        for result in results:
                if result.parameter.test_name not in title:
                    title.append(result.parameter.test_name)
#    parms = Parameter.objects.all()
    ret = ''
    ret += '''<table>\n<thead><tr>
            <th>Area</th>
            <th>Sampling point</th>
            <th>Tester</th>
            '''
#    for i in parms:
    for i in title:
        ret += '<th>%s</th>'% i

    ret +=       '''
            </tr></thead>
    '''
    count = 1
    if samples:
        for sample in samples:
                ret += '\n<tr class="%s">' % _get_class(count)
                count += 1
                point = sample.sampling_point
                ret += '<td>%s</td>' % (point.wqmarea)
                ret += '<td>%s</td>' % (point)
                ret += '<td>%s</td>' % (sample.taken_by)
                results = MeasuredValue.objects.filter(sample=sample)
                if results:
                    for result in results:
                        ret += '<td>'
                        ret += '%s ' % (result.value)
                        ret += '</td>'
                else:
                    ret += '<td>%s</td>' % ('No parameter for this submited sample')
                    
                ret += '</tr>'
    else:
        ret += '<td>No samples submitted</td>'
    ret += '</tbody></table>'
    return ret
