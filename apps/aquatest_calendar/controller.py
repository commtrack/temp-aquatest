import eventCalBase
from samples.models import *
import calendar



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

        temp = filter_samples(0,month,year,0)
        if temp:    # either 1 record or no record , check models.py
            self.db_cal = temp[0]

            if self.area == 0:
                self.db_events = filter_samples(0,month,year,self.area)
            else:
                self.db_events = filter_samples(0,month,year,self.area)
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
                        a = filter_samples(day,self.curr.month,self.curr.year,0)
                    else:
                        a = filter_samples(day,self.curr.month,self.curr.year,self.area)
                    total = a.count()
                    #assigns td name to be used by css to put color
                    abnormal = get_normality(day,self.curr.month,self.curr.year)
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
#
#here is the database interaction
#
def filter_samples(day,month,year,area):
    if area == 0 and month != 0 and day != 0:
        a = Sample.objects.filter(date_taken__day = day,
                    date_taken__month = month,
                    date_taken__year = year)
    elif area != 0 and day != 0:
        a = Sample.objects.filter(date_taken__day = day,
                            date_taken__month = month,
                            date_taken__year = year,
                            sampling_point__wqmarea__id = area
                            )
    elif day == 0 and area == 0:
        a = Sample.objects.filter(date_taken__year=year, date_taken__month=month)
    elif day ==0 and area != 0:
        b = Sample.objects.filter(date_taken__year=year, date_taken__month=month)
        a = b.filter(sampling_point__wqmarea = area)
    return a

def get_normality(day,month,year):
    samples = Sample.objects.filter(date_taken__day = day,
                    date_taken__month = month,
                    date_taken__year = year)
    check = []
    for sa in samples:
        set = 0
        resul = MeasuredValue.objects.filter(sample = sa)
        for resu in resul:
            a = NormalRange.objects.filter(value_rule__parameter = resu.parameter)
            for kk in a:
                #normal
                if float(kk.minimum) <=  float(resu.value) and float(resu.value) <= float(kk.maximum):
                    pass
                else:#abnormal
                    set = set + 1
        if set >= 1:
            check.append(1)
#1 for 0 abnormal samples
#2 for 1 abnormal sample
#3 for more than 1 abnormal
    if len(check) == 0:
        normality = 1
    elif len(check) == 1:
        normality = 2
    else:
        normality = 3
    return normality