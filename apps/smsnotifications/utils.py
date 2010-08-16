import httplib, urllib
from threading import Thread

from django.db import models
from django.db.models.signals import post_save

from smsnotifications.models import SmsNotification

def _send_sms(reporter_id, message_text):
    data = {"uid":  reporter_id,
            "text": message_text
            }
    encoded = urllib.urlencode(data)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    try:
        conn = httplib.HTTPConnection("localhost:8000") # TODO: DON'T HARD CODE THIS!
        conn.request("POST", "/ajax/messaging/send_message", encoded, headers)
        response = conn.getresponse()
    except Exception, e:
        # TODO: better error reporting
        raise

def send_sms_notifications(this_sample, its_values):
    # TODO: Lookup the reporters based on the sample point and
    # figure out who to send to, what to send
    # print sender.notes 
    reporter = this_sample.taken_by
    point = this_sample.sampling_point

    # A temporary SMS Response to the submitter
    # TODO: Auto generate response SMS.
    msg = "Aquatest: Your sample data is submitted successfully.!"
    thread = Thread(target=_send_sms,args=(reporter.id, msg ))
    thread.start()

    # create massage for the authorised testers.
    # sample sms: Test taken at site Borehole - Brandvlei. H2S positive Comment: Am out of chlorine
    msg2 = "Test taken at site %s - %s." % (this_sample.sampling_point.wqmarea, this_sample.sampling_point)
    for val in its_values:
        msg2 += " %s:%s" % (val.parameter.test_name, val.value)
    msg2 += '. Comment: %s'%(this_sample.notes)

    # find out who to send SMS to in the notification table.
    notices = SmsNotification.objects.filter(sampling_point = point)
    for notice in notices:
        reporter = notice.authorised_sampler
        # send SMS only when their is an abnormal values in the sample
        if notice.failure_notification == True:
            # Check sample contains abnormal value
            if get_normality(this_sample):
                # send the SMS to authorized personnel
                thread = Thread(target=_send_sms,args=(reporter.id, msg2 ))
                thread.start()
        else:
            # send the SMS to authorized personnel
            thread = Thread(target=_send_sms,args=(reporter.id, msg2 ))
            thread.start()

def get_normality(this_sample):
    # import for functions, required when the functions is called 
    # in other modules. apart from samples.models
    from samples.models import MeasuredValue, NormalRange
    
    set = 0
    results = MeasuredValue.objects.filter(sample = this_sample)
    for result in results:
        a = NormalRange.objects.filter(value_rule__parameter = result.parameter)
        for kk in a:
            # Normal
            if kk.minimum <  int(result.value) and int(result.value)  < kk.maximum:
                pass
            else:
                # Abnormal
                set = set + 1
    if set >= 1:
        check = True
    else:
        check = False
    return check