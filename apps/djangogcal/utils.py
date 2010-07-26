import calendar
from reportlab.pdfbase.pdfdoc import count
from datetime import datetime, timedelta
from samples.models import Sample

try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time



def today():
    """
        returns today date
    """
    today = datetime.date()

    return today

def  this_year():
    """
    returns this year
    """
    year = datetime.year()
    return year

def get_month_days(month=None):
    months = [31,28,31,30,31,30,31,31,30,31,30,31]
    month_days = month -1
    return months[month_days]


def get_month_name(month):
    month_names = [ 'January',
                    'February',
                    'March',
                    'April',
                    'May',
                    'June',
                    'July',
                    'August',
                    'September',
                    'October',
                    'November',
                    'December',
                    ]
    # correcting month number to read on a list
    this_month = month - 1
    return month_names[this_month]

def get_sample_by_date(date,month,year):
    """
    returns one samples as are sected on the calender
    """
    data = Sample.objects.filter(date_taken__day=date,
                                date_taken__month=month,
                                date_taken__year=year
    )

    return data


def get_month_samples(month, year):
    """
    returns monthly data to display on the calender
    """


    data = Sample.objects.filter(   date_taken__month=month,
                                    date_taken__year=year)
    return data

def get_data_startdate_enddate(stday,stmonth,styear,endday,endmonth,endyear):
    """
    this gives range of data samples for given date rage
    """
    data = Sample.objects.filter(
                                    date_taken__day=stday
    )

    return data

def get_data_sample_point(point):
    data = Sample.oblects.filter(
    sampling_point=point,
    )
    return data

def get_total_sample_day(date,month,year):
    data = Sample.objects.filter(date_taken__day=date,
                                date_taken__month=month,
                                date_taken__year=year
            ).count

    return data

def get_total_in_month(month,year):
    month_range=calendar.monthrange(year,month)
    
    totals = []
    for date in range(month_range[0],emonth_range[1]):
        data = Sample.objects.filter(date_taken__day=date,
                                    date_taken__month=month,
                                    date_taken__year=year
                ).count
        totals.append(data) # totals[date] = data

"""
________________________________________________________________________________
These methosds interface google calender
________________________________________________________________________________
"""

def update_events():

    pass

def insert_single_event(calendar_service, title='One-time Tennis with Beth', 
                      content='Meet for a quick lesson', where='On the courts', 
                      start_time=None, end_time=None):
    event = gdata.calendar.CalendarEventEntry()
    event.title = atom.Title(text=title)
    event.content = atom.Content(text=content)
    event.where.append(gdata.calendar.Where(value_string=where))

    if start_time is None:
      # Use current time for the start_time and have the event last 1 hour
      start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
      end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
    event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
    
    new_event = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')
    
    print 'New single event inserted: %s' % (new_event.id.text,)
    print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
    print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
    
    return new_event
