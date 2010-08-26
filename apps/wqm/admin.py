from django.contrib.gis import admin
from django.contrib.gis.maps.google import GoogleMap

from hq.models import *
from wqm.models import WqmAuthority,WqmArea,SamplingPoint,DeliverySystem

GMAP = GoogleMap(key='ABQIAAAAwLx05eiFcJGGICFj_Nm3yxSy7OMGWhZNIeCBzFBsFwAAIleLbBRLVT87XVW-AJJ4ZR3UOs3-8BnQ-A') # Can also set GOOGLE_MAPS_API_KEY in settings

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

class SamplingPointAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
        }),
        (None, {
            'fields' : ('point_type', 'delivery_system','treatment')
        }),
        ('Map', {
            'fields' : ('point',)
        }),
    )
admin.site.register(SamplingPoint, SamplingPointAdmin)
#admin.site.register(SamplingPoint, admin.GeoModelAdmin)


admin.site.register(DeliverySystem)

class SamplingPointAdminGoogle(admin.OSMGeoAdmin):
    #extra_js = [GMAP.api_url + GMAP.key]
    #map_template = 'wqm/admin/google.html'
    
    list_display = ('name', 'wqmarea', 'modified', 'created')
    search_fields = ('name', 'wqmarea', 'modified', 'created')
    list_filter = ['name']
    fieldsets = (
        (None, {
            'fields' : ('name', 'code', 'wqmarea', 'modified', 'created')
        }),
        (None, {
            'fields' : ('point_type', 'delivery_system','treatment')
        }),
        ('Map', {
            'fields' : ('point',)
        }),
    )
# Register the google enabled admin site
google_admin = admin.AdminSite()
google_admin.register(SamplingPoint, SamplingPointAdminGoogle)

# Getting an instance so we can generate the map widget; also
# getting the geometry field for the model.
admin_instance = SamplingPointAdminGoogle(SamplingPoint, admin.site)
point_field = SamplingPoint._meta.get_field('point')

# Generating the widget.
PointWidget = admin_instance.get_map_widget(point_field)
