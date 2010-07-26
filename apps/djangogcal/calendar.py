from django.db import models
from datetime import datetime
try:
  from xml.etree import ElementTree
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
from samples.models import *
#from samples.models import count_samples


def abnormal_rage():
    """
    this query for today samples with abnormal ranges
    """

    count_abnormal_range = 1
    return count_abnormal_range


def send_event_google_calender(where,tetr,parms):
    cal_client = gdata.calendar.service.CalendarService()
    cal_client.email = 'aquatest.project@gmail.com'
    cal_client.password = 'admin1234xy'
    cal_client.source = 'Google-Calendar_Python_Sample-1.0'
    cal_client.ProgrammaticLogin()
#    count = count_samples()
    count =1
    tester =tetr
    parameters = parms
    title = ("%s. %s") % (count,where)
    content = ("Tester is : %s <p> Parameters are : %s</p>")  % (tester,parameters)
    atime = time.gmtime()
    stime = time.gmtime(time.time() + 3600)
    cal_path = '/calendar/feeds/aquatest.project@gmail.com/private/full'

    event = gdata.calendar.CalendarEventEntry()
    event.title = atom.Title(text=title)
    event.content = atom.Content(text=content)
    event.where.append(gdata.calendar.Where(value_string=where))

    # Use current time for the start_time and have the event last 1 hour
    start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', atime)
    end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', stime)
    event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))

    new_event = cal_client.InsertEvent(event, cal_path)
    return new_event
