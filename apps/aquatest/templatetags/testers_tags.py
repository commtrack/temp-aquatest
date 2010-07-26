import datetime
from django import template

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from types import ListType,TupleType

from xformmanager.models import *
import xformmanager.adapter.querytools as qtools
from hq.models import *
import hq.utils as utils
from datetime import timedelta
import graphing.dbhelper as dbhelper
from hq.models import *
from reporters.models import Reporter
from samples.models import Sample
register = template.Library()

from graphing.models import RawGraph

import time

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'



@register.simple_tag
def get_counts_for_tester(reporter):
    # Getting the count on the number of samples the user have submited
    # this last month and the total count all time.

    delta = timedelta(days=30)
    enddate = datetime.today()
    startdate = enddate - delta
    count_hash_month = {}
    count_hash_total = {}
    
    ret =""
       
    count_month = Sample.objects.filter(taken_by=reporter, date_received__gte = startdate, date_received__lte = enddate ).count()
    count_hash_month[reporter] = count_month

    count_total = Sample.objects.filter(taken_by=reporter).count()
    count_hash_total[reporter] = count_total

    
    
    ret += '<td>%s</td>' % (count_hash_month[reporter])
    ret += '<td>%s</td>' % (count_hash_total[reporter])

    return ret

@register.simple_tag
def _get_class(count):
    if count % 2 == 0:
        return "even"
    return "odd"
 