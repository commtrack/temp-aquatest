import calendar, datetime
import copy

#
# This modules handles calendar events
#

class monthCalendar(object):
    """Month Calendar"""
    def __init__(self, owner, year, month):
        if self.checkYMD(year, month, 1):
#            self.id = id
            self.owner = owner
            self.year = year
            self.month = month
            self.calendar = calendar.monthcalendar(year, month)
            self.events = {}
        else:
            raise ValueError, ('year (%s) or month (%s) out of range' % (
                    year, month))

    def getDate(self, day):
        return datetime.date(self.year, self.month, day)

    def checkYMD(self, year, month, day):
        """check range of year, month and day.  Raise ValueError on error.
            Return True otherwise"""
        datetime.date(year, month, day)
        return True

    def getDailyEvents(self, day=datetime.datetime.now().day):
        """Return all events for 'day', default as today"""
        result = []
        if day in self.events:
            result = self.events[day]
        return result

    def getEvents(self, day=datetime.datetime.now().day, 
            time=datetime.time()):
        """Return a list of event in specific day and time, [] if no event
            matches"""
        dayEvents = self.getDailyEvents(day)
        dayEventsDatetime = map(lambda x: x.start, dayEvents)

        result = []
        index = 0
        target = datetime.datetime.combine(self.getDate(day), time)
        for c in xrange(dayEventsDatetime.count(target)):
            index = dayEventsDatetime[index:].index(target)
            result.append(dayEvents[index])
        return result

    def addEvent(self, event, day=datetime.datetime.now().day):
        """add event to day.  'event' is expected to support interface
            of event()"""
        nevent = copy.deepcopy(event)
        if self.checkYMD(1, 1, day):
            if day in self.events:
                self.events[day].append(nevent)
            else:
                self.events[day] = [nevent]

            # adjust date of nevent
            date = self.getDate(day)
            self.events[day][-1].setStart(
                    datetime.datetime.combine(date, nevent.getStart().time()))
            # finally, sort events for 'day'
            self.events[day].sort()
        
class event(object):
    """A Event object that is time aware,area and total count.  Time resolution of event is
        up to second."""
    def __init__(self, id, name, start=datetime.datetime.now(), desc=''):
        """defailt date is now()"""
        if self.checkDate(start):
            self.id = id
            self.name = name
            self.desc = desc
            self.total = None
            self.area = None
            self.start = self.adjustDatetime(start)
        else:
            raise ValueError, '%s.  Expected datetime object' % start

    def __str__(self):
        return '<Event (%s) starts at %s>' % (self.name, self.start)

    def __repr__(self):
        return "event('%s', %s, '%s')" % (self.name, self.start, self.desc)

    def __eq__(self, other):
        # Note: self.desc is not compared
        result = False
        try:
           result = self.id == other.id
        except:
            pass
        return result

    def __lt__(self, other):
        return self.start < other.start

    def __gt__(self, other):
        return not (self < other or self == other)
    def __ge__(self, other):
        return not (self < other) or self == other
    def __le__(self, other):
        return not self > other
    def __ne__(self, other):
        return not self == other

    def adjustDatetime(selfi, datetime):
        """adjust datetime to second level (ignore microsecond)"""
        return datetime.replace(microsecond=0)
        
    def checkDate(self, data):
        """check True if data supports datetime.datetime interface, False
            otherwise"""
        try:
            for attr in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                getattr(data, attr)
        except AttributeError: 
            return False
        return True

        datetime.date(year, month, day)
        return True

    def getStart(self):
        return self.start
    def setStart(self, datetime):
        """change start datetime of event"""
        self.start = datetime
        
    def passDue(self, datetime):
        """return True if date + time > self.date + self.time, False oterwise"""
        # time can be datetime or date or time
        return self < event(0, '', datetime)


