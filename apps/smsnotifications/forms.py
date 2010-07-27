from django import forms
from django.forms import ModelForm
from smsnotifications.models import SmsNotification

class SmsNotificationForm(ModelForm):
    class Meta:
        model = SmsNotification
        exclude = ('modified','created',)