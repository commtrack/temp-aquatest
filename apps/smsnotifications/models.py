from datetime import datetime
import httplib, urllib
from threading import Thread

from django.db import models
from django.db.models.signals import post_save

from samples.models import *
from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import FormDefModel


# TODO: auto-create a notication choices as the xform is added to a domain.
# link the notification type to the xform
#NOTIFICATION_TYPE_CHOICES = (
#    (u'all', u'All'),
#    (u'http://www.aquatest-za.org/h2s', u'h2s'),
#    (u'http://www.aquatest-za.org/physchem', u'physchem'),
#)

class NotificationChoice(models.Model):
    choice = models.CharField(max_length=255)
    xform = models.ForeignKey(FormDefModel)

    def __unicode__(self):
        return self.choice

class SmsNotification(models.Model):
    sampling_point = models.ManyToManyField(SamplingPoint, help_text="Hold down Ctrl for multiple selections")
    authorised_sampler = models.ForeignKey(Reporter)
    # TODO: Notification should be selected from the type of xforms.
    notification_type = models.ForeignKey(NotificationChoice)
    failure_notification = models.BooleanField(default=False, help_text="select if you want to send sms only when value is out of range")
    digest = models.BooleanField(default=False)
    modified = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now())
    
    def __unicode__(self):
            return '%s notification for %s'%(self.notification_type, self.authorised_sampler)

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

def send_sms_notifications(sub, vals):
    # TODO: Lookup the reporters based on the sample point and
    # figure out who to send to, what to send
    # print sender.notes
    reporter = sub.taken_by
    point = sub.sampling_point

    # A temporary SMS Response
    # TODO: Auto generate response SMS.
    msg = "Aquatest: Your sample data is submitted sucessfully.!"
    # sending an sms to a submitter.
    thread = Thread(target=_send_sms,args=(reporter.id, msg ))
    thread.start()

    # create massage for the authorised testers.
    # sample sms: Test taken at site Borehole - Brandvlei. H2S positive Comment: Am out of chlorine
    msg2 = "Test taken at site %s - %s." % (sub.sampling_point.wqmarea, sub.sampling_point)

    for val in vals:
        msg2 += " %s:%s" % (val.parameter.test_name, val.value)

    msg2 += '. Comment: %s'%(sub.notes)

    # figure out who to send sms to in the notifation table.
    notices = SmsNotification.objects.filter(sampling_point = point)

    for notice in notices:
        reporter = notice.authorised_sampler
        # TODO: generate a sms according the the authorised tester.
        # this is temp sms to authorised sampler
        # send the sms
        thread = Thread(target=_send_sms,args=(reporter.id, msg2 ))
        thread.start()

