from datetime import datetime

from django.db import models

from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import FormDefModel

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