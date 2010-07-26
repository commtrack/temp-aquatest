from standards.models import Standard,WaterUseType
from django.contrib import admin
from hq.models import *
from resources.models import *
from django.contrib import admin

'''
customize
'''

class WaterUseTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'modified','created')
    search_fields = ('description', 'modified','created')
    list_filter = ['modified']
admin.site.register(WaterUseType, WaterUseTypeAdmin)

class StandardAdmin(admin.ModelAdmin):
    list_display = ('name','govering_body','date_effective','modified','created')
    search_fields = ('name','govering_body','date_effective','modified','created')
    list_filter = ['govering_body']
admin.site.register(Standard, StandardAdmin)

