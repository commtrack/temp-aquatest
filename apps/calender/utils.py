import calendar
from reportlab.pdfbase.pdfdoc import count
from datetime import datetime, timedelta
from samples.models import Sample

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
