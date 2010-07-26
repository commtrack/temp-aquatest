import datetime

from django.db import models
from django.contrib.auth.models import User

from domain.models import Domain
from locations.models import Location




#!Todo: Domain in the hp app is much similiar to the
#       the facility in the commtrack. hence a simple verbose
#       name will do the trick, to bring a bit of feeling and
#       slight tweek of the hq.model will be enuf to put the
#       facility and users in place.


class ResourceCategory(models.Model):
    '''
    This is the division of resources, in groups of similar traits. eg Furniture
    as a general category of all furnitures ie chairs, tables...
    '''
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Resource Category'
        verbose_name_plural = 'Resource Categories'

    def __unicode__(self):
        return self.name


# shuld the resource status be implentent in a class allowing manager
# to define the resource statuses,?
STATUS_CHOICES = (
    ('exellent',    'Exellent'),
    ('good',        'Good'),
    ('normal',      'Normal'),
    ('not_ok',      'Not Okey'),
    ('bad',         'Bad'),
)

class Resource(models.Model):
    '''
    A resource is an object with........
    '''
    name = models.CharField(max_length=50)
#   A resource can be in only one category this currently works.. but will change to ManyToMany
    category = models.ForeignKey(ResourceCategory, blank=True, null=True)
    code = models.CharField(max_length=256, help_text='unique identifier')

#   get a better understanding of domain in the hq.models Domain as it's looks a major classifer
#   of people/and things it's luks as an optoin to attach a resource to a domain rather than a
#   location (from Location app) but for now will attact it to both till a decision is made.
    location = models.ForeignKey(Location)
    domain  = models.ForeignKey(Domain)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField(null=True, blank=True)
    status_change_count = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=datetime.datetime.now())
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class TrackResource(models.Model):
    resource = models.ForeignKey(Resource)
    user = models.ForeignKey(User)
    date_tracked = models.DateTimeField(default=datetime.datetime.now())
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '%s : %s' % (self.resource, self.date_tracked)

class ResourceSupplyRequest(models.Model):
    user = models.ForeignKey(User)
    resource = models.ForeignKey(Resource)
    request_date = models.DateTimeField(default=datetime.datetime.now())
    request_remarks = models.TextField(null=True, blank=True)
#   since the resource/user is alredy afixed to a location it's seems like a
#   redundancy to put location in the supply form. BUT for now will leave this
    location = models.ForeignKey(Location)

    def __unicode__(self):
        return '%s' % (self.user)
    