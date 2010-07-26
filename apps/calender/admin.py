from django.contrib import admin
from calender.models import SyncEvents



class SyncEventsAdmin(admin.ModelAdmin):
    list_display = ('event_id','date','status')
    search_fields = ('event_id','date','status')
    list_filter = ['event_id','date','status']
admin.site.register(SyncEvents, SyncEventsAdmin)