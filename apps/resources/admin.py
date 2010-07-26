from django.contrib import admin
from hq.models import *
from django.contrib.auth.models import Group, User
from reporters.models import Reporter
from locations.models import Location
from resources.models import *

'''
'''
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category','domain')
    list_filter = ['domain', 'category', 'status']
    search_fields = ('name','code')
admin.site.register(Resource,ResourceAdmin)

class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(ResourceCategory,ResourceCategoryAdmin)

class TrackResourceAdmin(admin.ModelAdmin):
    list_display = ('resource', 'status', 'user', 'date_tracked')
    date_hierarchy = 'date_tracked'
    list_filter = ('status', 'date_tracked')
    search_fields = ('resource', 'user')
admin.site.register(TrackResource, TrackResourceAdmin)

class ResourceSupplyRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource', 'request_date')
    date_hierarchy = 'request_date'
    search_fields = ('user', 'resource')
#    list_filter = ['location']
admin.site.register(ResourceSupplyRequest,ResourceSupplyRequestAdmin)