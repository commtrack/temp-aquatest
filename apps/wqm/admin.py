from django.contrib import admin

from hq.models import *
from wqm.models import WqmAuthority,WqmArea,SamplingPoint

class WqmAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'modified', 'created')
    search_fields = ('name', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'modified', 'created')
        }),
    )
admin.site.register(WqmAuthority, WqmAuthorityAdmin)

class WqmAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'wqmauthority', 'modified', 'created')
    search_fields = ('name', 'wqmauthority', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'wqmauthority', 'modified', 'created')
        }),
    )
admin.site.register(WqmArea, WqmAreaAdmin)

class SamplingPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
        }),
        ('Coordinates', {
            'fields' : ('latitude', 'longitude')
        })
    )
admin.site.register(SamplingPoint, SamplingPointAdmin)


