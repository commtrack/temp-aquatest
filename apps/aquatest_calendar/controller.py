import eventCalBase
from samples.models import *
import calendar

#
# TODO - should have used id to identify event, not rowid
#

class CalendarController(object):
    """Controller object for calendar"""
    def __init__(self, day=1,q=0):
        """owner - owner of this calendar, day - day to shown"""
        calendar.setfirstweekday(calendar.SUNDAY)
        self.area = q
        self.day = day
        self.curr = None
        self.db_cal = None
        self.db_events = None

## database related operation (i.e. operation will sync with DB
    def load(self, year, month):
        """load calendar with data from database"""
        
        temp = Sample.objects.filter(date_taken__year=year, date_taken__month=month)
        if temp:    # either 1 record or no record , check models.py
            self.db_cal = temp[0]
            
            if self.area == 0:
                self.db_events = Sample.objects.filter(date_taken__year=year, date_taken__month=month)
            else:
                a = Sample.objects.filter(date_taken__year=year, date_taken__month=month)
                self.db_events = a.filter(sampling_point__wqmarea = self.area)
            self.curr = eventCalBase.monthCalendar(self, year, month)
#put events to map a month
            for db_e in self.db_events:              
                e = eventCalBase.event(db_e.id, db_e.taken_by,db_e.date_taken, db_e.sampling_point)
                self.curr.addEvent(e, db_e.date_taken.day)
        else:
            self.curr = eventCalBase.monthCalendar(None,
                    year, month)


## functions used by template
    def next(self):
        """return a tuple that contains next year and month"""
        y = self.curr.year
        m = self.curr.month
        if m == 12:
            m = 1
            y += 1
        else:
            m += 1
        return (y,m)
        
    def prev(self):
        """return a tuple that contains previous year and month"""
        y = self.curr.year
        m = self.curr.month
        if m == 1:
            m = 12
            y -= 1
        else:
            m -= 1
        return (y,m)
        
    def getWeekHeader(self):
        """return a list of week header"""
        return calendar.weekheader(2).split()

    def getMonthHeader(self):
        """return a tuple that contains abbv. month name and 4 digit year"""
        return self.curr.getDate(1).strftime("%b"), self.curr.year
#put counts on the calendar
    def getMonthCalendar(self):
        """return a matrix similar to calendar.monthCalendar().  Except
           the element is replaced by (day, event exist,count)"""
        res = []
        for dayline in calendar.monthcalendar(self.curr.year, self.curr.month):
            res_line = []
            for day in dayline:
                data = False
                total = 0
                abnormal = 0
                if day in self.curr.events:
                    data = True
                    if self.area == 0:
                        a = Sample.objects.filter(date_taken__day = day,
                                    date_taken__month = self.curr.month,
                                    date_taken__year = self.curr.year)
                    else:
                        a = Sample.objects.filter(date_taken__day = day,
                                            date_taken__month = self.curr.month,
                                            date_taken__year = self.curr.year,
                                            sampling_point__wqmarea__id = self.area
                                            )
                    total = a.count()
##
#Write a function here that assign number to abnormal due to being in abnormal range
#wait for abnormal range fixing issue
##
                    abnormal = 1
                res_line.append((day, data, total,abnormal))
            res.append(res_line)
        return res
        
    def getDailyEvents(self):
        """return list of events for the day"""
        return self.curr.getDailyEvents(self.day)

    def hasDailyEvents(self):
        """return list of events for the day"""
        return len(self.curr.getDailyEvents(self.day)) > 0

    def getDayName(self):
        result = 'th'
        if self.day % 10 == 1 and self.day != 11:
            result = 'st'
        elif self.day % 10 == 2 and self.day != 12:
            result = 'nd'
        elif self.day % 10 == 3 and self.day != 13:
            result = 'rd'
        return result
