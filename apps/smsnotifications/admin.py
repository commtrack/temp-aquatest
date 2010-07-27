from smsnotifications.models import SmsNotification, NotificationChoice
from django.contrib import admin
from hq.models import *

class SmsNotificationAdmin(admin.ModelAdmin):
    list_display = ('authorised_sampler', 'notification_type','digest','modified','created')
    search_fields = ('sampling_point', 'authorised_sampler', 'notification_type','digest','modified','created')
    list_filter = ['sampling_point', 'authorised_sampler', 'notification_type']
admin.site.register(SmsNotification,SmsNotificationAdmin)

class NotificationChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice', 'xform')
admin.site.register(NotificationChoice,NotificationChoiceAdmin)
