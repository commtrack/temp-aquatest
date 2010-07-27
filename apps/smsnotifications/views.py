import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta
from graphing import dbhelper

from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.exceptions import *
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django import forms

from rapidsms.webui.utils import render_to_response, paginated
#from rapidsms.reporters.models import *

from xformmanager.models import *
from hq.models import *
from graphing.models import *
from receiver.models import *

import hq.utils as utils
import hq.reporter as reporter
import hq.reporter.custom as custom
import hq.reporter.metastats as metastats

import hq.reporter.inspector as repinspector
import hq.reporter.metadata as metadata

from domain.decorators import login_and_domain_required
from reporters.utils import *
from reporters.views import message, check_reporter_form, update_reporter
from reporters.models import Reporter, PersistantBackend, PersistantConnection
from locations.models import Location, LocationType
from wqm.models import WqmAuthority, SamplingPoint
from smsnotifications.models import SmsNotification, NotificationChoice

from django import forms
from django.forms import ModelForm

logger_set = False

class SmsNotificationForm(ModelForm):
    class Meta:
        model = SmsNotification
        exclude = ('modified','created',)

@login_and_domain_required
def index(request):
    template_name = 'sindex.html'

    notifications = SmsNotification.objects.all().order_by("-authorised_sampler")
    points = SamplingPoint.objects.all().order_by("name")
    districts = WqmAuthority.objects.all()

    return render_to_response(request,
        template_name, {
        "notifications": paginated(request, notifications, prefix="smsnotice"),
        "points" : points,
        "districts":    districts,
    })


@login_and_domain_required
def delete_notifications(req, pk):
    notification = get_object_or_404(SmsNotification, pk=pk)
    notification.delete()

    transaction.commit()
    id = int(pk)
    return message(req,
        "SMS Notification %d deleted" % (id),
        link="/smsnotification")

def check_notice_form(req):

    # verify that all non-blank
    # fields were provided
    missing = [
        field.verbose_name
        for field in SmsNotification._meta.fields
        if req.POST.get(field.name, "") == ""
           and field.blank == False]

    # simple hack to removed a created date in the missing field
    # it's not null but auto-created.
    if 'created' in missing:
        index = missing.index('created')
        del missing[index]

    exists = []
    point = req.POST.get("sampling_point","")
    tester = req.POST.get("authorised_sampler","")
    notice_type = req.POST.get("notification_type","")
    if SmsNotification.objects.filter( sampling_point = point, authorised_sampler = tester, notification_type = notice_type  ):
        exists = ['SmsNotification']

    # TODO: add other validation checks,
    # or integrate proper django forms
    return {
        "missing": missing,
        "exists": exists }

def comma(string_or_list):
    """ TODO - this could probably go in some sort of global util file """
    if isinstance(string_or_list, basestring):
        string = string_or_list
        return string
    else:
        list = string_or_list
        return ", ".join(list)

def get_tester(current_user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    rep_profile = ReporterProfile.objects.filter(domain=current_user.selected_domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters

@login_and_domain_required
def add_notifications(request):
    template_name = "sms-notifications.html"
    if request.method == 'POST': # If the form has been submitted...
        form = SmsNotificationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            form.save()
            return message(request,
                        "SMS Notification Added",
                        link="/smsnotification")
    else:
        form = SmsNotificationForm() # An unbound form

    return render_to_response(request,template_name, {
        'form': form,
    })

@login_and_domain_required
def edit_notifications(request, pk):
    template_name = "sms-notifications.html"
    notification = get_object_or_404(SmsNotification, pk=pk)
    if request.method == 'POST': # If the form has been submitted...
        form = SmsNotificationForm(request.POST, instance = notification) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # saving the form data is not cleaned
            form.save()
            return message(request,
                        "SMS Notification Updated",
                        link="/smsnotification")
    else:
        form = SmsNotificationForm(instance=notification)
    
    return render_to_response(request,template_name, {
        'form': form,
        'notification': notification,
    })
