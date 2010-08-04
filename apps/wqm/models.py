import datetime

from django.contrib.gis.db import models

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

class DeliverySystem(models.Model):
    name = models.CharField(max_length=100, 
                            help_text="house connection, public tap, borehole, protected spring, unprotected spring, river, dam or lake, reservoir,distribution system")
    
    def __unicode__(self):
        return self.name

class SamplingPoint(WqmLocation):
    """ The point the tests are done """
    
    POINT_TYPE_CHOICES = (
                                  ("ground", "Ground"),
                                  ("surface","Surface"),
                                  )
    TREATMENT_CHOICES = (
                          ('treated', 'Treated'),
                          ('untreated', 'Untreated'),
                          )
    wqmarea = models.ForeignKey(WqmArea)
    point_type = models.CharField(max_length=30, choices=POINT_TYPE_CHOICES)
    delivery_system = models.ForeignKey(DeliverySystem)
    treatment = models.CharField(max_length=30, choices=TREATMENT_CHOICES)
    point = models.PointField(blank=True)
    
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name
