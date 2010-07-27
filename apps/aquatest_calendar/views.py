from rapidsms.webui.utils import render_to_response, paginated
from xformmanager.models import *
from wqm.models import *
from hq.models import *
from graphing.models import *
from receiver.models import *
from domain.decorators import login_and_domain_required
from reporters.utils import *
from samples.models import *
import datetime, calendar
import copy
from aquatest_calendar.controller import CalendarController
from wqm.models import WqmArea
logger_set = False

@login_and_domain_required
def view(request):
    """Calendar view"""

    user = request.user

    date = datetime.datetime.now()
    default = dict(month=date.month, year=date.year, day=1, rowid=1,
            name="", desc="", when="", area = 0)
    url = request.path
    p = getParams(request, default)
    year, month, day,area = p['year'], p['month'], p['day'], p['area']
    search_string = WqmArea.objects.all()
    location_name = WqmArea.objects.filter(id = area)    
    cal = CalendarController(day, area)
    cal.load(year, month)
    template_name="calendar.html"
    context = {}
    dict(username=user, cal=cal, url=url)
    i = 0
    context = {
        "username":user,
        "cal":cal,
        "url":url,
        "area":area,
        "search_string":search_string,
        'i':i,
        "location_name":location_name
    }
    return render_to_response(request, template_name, context)

## helper function
def getParams(request, default):
    """get parameter (case insensitive for key) (support both get and post)
        param is updated as side effect (for now)"""
    paramKeys = ['year', 'month', 'day', 'rowid', 'name', 'desc', 'when','area']
    paramFunc =  [int, int, int, int, str, str, str, int ]
    paramDef = dict(zip(paramKeys, paramFunc))

    inputDict = getattr(request, request.method, {})
    result = copy.deepcopy(default)
    for k in inputDict:
        kl = k.lower()
        if kl in default and kl in paramDef:
            try:
                result[kl] = paramDef[kl](getattr(request, request.method)[k])
            except KeyError:
                pass
    return result

@login_and_domain_required
def sample_popup(request):
    """Popup (compact) view a group of forms for a particular xmlns.
       Used in modal dialogs."""
#    group = FormDefModel.get_group_for_namespace(request.user.selected_domain, xmlns)
    return render_to_response(request, "xformmanager/xmlns_group_popup.html",
                             {"user": user})

def get_count(day,month,year,area):
    if area == 0:
        samples = Sample.objects.filter(date_taken__day = day,
                                    date_taken__month = month,
                                    date_taken__year = year)
    else:
        a = Sample.objects.filter(date_taken__day = day,
                                    date_taken__month = month,
                                    date_taken__year = year)
        samples = a.filter(sampling_point__wqmarea = area)
    count = samples.count()
    return count

@login_and_domain_required
def samples_pop(request):
    """Popup (compact) view a group of samples for a particular day.
    """
    date =  request.REQUEST.get("date","").split('-')
    year = int(date[0])
    month = int(date[1]) - 1
    day = int(date[2])
    area = int(date[3]) 
    count =  get_count(day,month,year,area)
    date = "%s-%s-%s" % (year,month,day)

    template_name="sample_popup.html"
    context = {}
    context = {
        "year":year,
        "month": month,
        "day":day,
        "count": count,
        "date":date,
        "area":area
 
    }


    return render_to_response(request, template_name,context)