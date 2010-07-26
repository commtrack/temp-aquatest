import datetime
from django.db import models

from locations.models import Location


class WqmLocation(Location):
    """
    For this module, we add a created and modified date to 
    our locations.
    """ 
    modified = models.DateTimeField(blank=True,null=True)
    created = models.DateTimeField(default=datetime.datetime.now())

class WqmAuthority(WqmLocation):
    """E.g. a district"""
    
    def __unicode__(self):
        return self.name

class WqmArea(WqmLocation):
    wqmauthority = models.ForeignKey(WqmAuthority)
    
    def __unicode__(self):
        return self.name

class SamplingPoint(WqmLocation):
    """ The point the tests are done """
    wqmarea = models.ForeignKey(WqmArea)

    def __unicode__(self):
        return self.name
