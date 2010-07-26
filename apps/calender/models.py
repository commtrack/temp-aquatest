from django.db import models




class SyncEvents(models.Model):
    event_id = models.CharField(max_length=250, null=True, blank=True)
    date = models.DateTimeField()
    status = models.BooleanField(default=False)
#    failed = models.BooleanField(default=False)


