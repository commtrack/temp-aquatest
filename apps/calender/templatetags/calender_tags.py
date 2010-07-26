import datetime
from django import template

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from types import ListType,TupleType

from datetime import timedelta
import graphing.dbhelper as dbhelper
from reporters.models import Reporter
from hq.models import *
from reporters.models import Reporter
from samples.models import *
from wqm.models import *
from django import template
from datetime import datetime
from calender.utils import *
#register = template.Library()
register = template.Library()
import time

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'

@register.simple_tag
def calender_view(month):
    month_name = get_month_name(month)
#    year = this_year()
    table = '<h1>%s</h1>'% (month_name)
    end = get_month_days(month)+1
#    for day in range(1, end):
#        table += '<a href =''><li> %s </li></a>' % day

#    table += '<table border="1">'
#    table +=  '<thead><tr>'
##    table +=  '<th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th><th>Sunday</th> </tr> </thead><tbody><tr>'
#    table +=  '<th></th><th></th><th></th><th></th><th></th><th></th><th></th> </tr> </thead><tbody><tr>'
#    table +=  '<td></td>'
#    table +=  '<td></td>'
#    table +=  '</tr><tr>'
#    table +=  '<td></td>'
#    table +=  '<td></td>'
#    table +=  '</tr></tbody></table>'

    count = 1
    table += '<table>'
    table += '<tr>'
    for day in range(1, end):
        table += '<td value="%s" id ="%s"><a href ="#">%s</a></td>' % (day, day, day)
        if count >= 7:
            table += '</tr>'
            table += '<tr>'
            count = 0
        count = count + 1
    table += '</table>'
    return table

def _get_class(count):
    if count % 2 == 0:
        return "even"
    return "odd"

@register.simple_tag
def get_tester(user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    rep_profile = ReporterProfile.objects.filter(domain=user.selected_domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters

@register.simple_tag
def get_all_samples_rage(user):
    # TODO: Get all the tester in the same domain and display them
    # with the total samples.
    testers = get_tester(user)

    ret = ''
    ret += '''<table>\n<thead><tr>
            <th>Date Taken</th>
            <th>Sampling point (Area)</th>
            <th>Tester</th>
            <th>Parameters</th></tr></thead>'''


    # samples are listed accourding to the tester,
    # wheras according to the received date is more appropriate.
    samples = []
    for tester in testers:
        some_samples = Sample.objects.filter(taken_by=tester)
        samples.extend(some_samples)

    ret += '<tbody>'
    count = 1
    if samples:
        for sample in samples:
            ret += '\n<tr class="%s">' % _get_class(count)
            count += 1
            point = sample.sampling_point
            ret += '<td>%s</td>' % (sample.date_taken)
            ret += '<td>%s (%s)</td>' % (point, point.wqmarea)
            ret += '<td>%s</td>' % (sample.taken_by)


#            ret += '<td>%s</td>' % (sample.date_received)

            # TODO: Get the results for the sample and
            # present it in a gud way.
            results = MeasuredValue.objects.filter(sample=sample)
            if results:
                ret += '<td>'
                for result in results:
                    ret += '%s %s, ' % (result.value, result.parameter.test_name_short)
                ret += '</td>'
            else:
                ret += '<td>%s</td>' % ('No parameter for this submited sample')
            ret += '</tr>'
    else:
        ret += '<td>No samples submitted</td>'
    ret += '</tbody></table>'
    return ret






#@register.simple_tag
@register.filter(name='calendar_table')
def calendar_table(value, arg):
  cal = {}
  dates = value.keys()
  dates.sort()
  for date in value:
    d, m, y = date.day, date.month, date.year
    if y not in cal:
      cal[y] = {}
    if m not in cal[y]:
      cal[y][m] = []
    cal[y][m].append(d)
  result = ''

  for y in cal:
    result += "<h2 style=\"clear: left\">%d</h2>" % y
    for m in cal[y]:
      sd = datetime(y, m, 1)
      result += sd.strftime("<div class=\"month\"><h3>%B</h3>")
      result += '<table><thead><tr><th>M</th><th>T</th><th>W</th><th>T</th><th>F</th><th>S</th><th>S</th></tr></thead><tbody><tr>'
      days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m]
      if m == 2 and y % 4 == 0 and (y % 100 <> 0 or y % 400 == 0):
        days_in_month += 1
      w = sd.weekday()
      for i in range(w):
        result += '<td></td>'

      for i in range(days_in_month):
        if i in cal[y][m]:
          s = arg.replace('[Y]', "%.4d" % y).replace('[m]', "%.2d" % m).replace('[d]', "%.2d" % d)
          result += "<td><a href=\"%s\">%d</a></td>" % (s, i + 1)
        else:
          result += "<td>%d</td>" % (i + 1)
        w = (w + 1) % 7
        if w == 0 and i + 1 < days_in_month:
          result += "</tr><tr>"

      for i in range(w,7):
        result += '<td></td>'

      result += '</tr></tbody></table></div>'
  return result
