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
register = template.Library()

from graphing.models import RawGraph

import time

from samples.models import *
from wqm.models import *

xmldate_format= '%Y-%m-%dT%H:%M:%S'
output_format = '%Y-%m-%d %H:%M'



@register.simple_tag
def m_values(this_sample):
    # TODO: Get all the tester in the same domain and display them
    # with the total samples.
    
    ret = ''
    results = MeasuredValue.objects.filter(sample= this_sample)
    if results:
        ret += '<td>'
        for result in results:
            ret += '%s %s%s, <br />' % (result.parameter.test_name, result.value,result.parameter.unit)
        ret += '</td>'
    else:
        ret += '<td>%s</td>' % ('No parameter for this submitted sample')
    
    return ret
