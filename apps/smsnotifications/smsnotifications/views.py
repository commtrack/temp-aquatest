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

logger_set = False


@login_and_domain_required
def index(request):
    template_name = 'sindex.html'

    notifications = SmsNotification.objects.all()
    points = SamplingPoint.objects.all()
    districts = WqmAuthority.objects.all()

    return render_to_response(request,
        template_name, {
        "notifications": paginated(request, notifications, prefix="smsnotice"),
        "points" : points,
        "districts":    districts,
    })

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def add_notifications(req):

    def get(req):
        template_name = "sms-notifications.html"
        notifications = SmsNotification.objects.all()
        districts = WqmAuthority.objects.all()
        points = SamplingPoint.objects.all()
        testers = get_tester(req.user)
        return render_to_response(req,
                template_name, {
                "notifications": paginated(req, notifications, prefix="smsnotice"),
                "points" : points,
                "districts" : districts,
                "testers" : testers,
                "notification_types_choices" : NotificationChoice.objects.all(),
            })

    @transaction.commit_manually
    def post(req):
        # check the form for errors
        notice_errors = check_notice_form(req)

        # if any fields were missing, abort.
        missing = notice_errors["missing"]
        exists = notice_errors["exists"]

        if missing:
            transaction.rollback()
            return message(req,
                "Missing Field(s): %s" % comma(missing),
                link="/smsnotification/add")
        # if authorised tester with same notification and point exists, abort.
        if exists:
            transaction.rollback()
            return message(req,
                "%s already exist" % comma(exists),
                link="/smsnotification/add")

        try:
            # create the notification object from the form
            notification = SmsNotification()

            rep = Reporter.objects.get(pk = req.POST.get("authorised_sampler",""))
            notification.authorised_sampler = rep

            choice = NotificationChoice.objects.get(pk = req.POST.get("notification_type",""))
            notification.notification_type = choice

            point = SamplingPoint.objects.get(pk = req.POST.get("sampling_point",""))
            notification.sampling_point = point

            notification.digest = req.POST.get("digest","")

            
            # save the changes to the db
            notification.save()
            transaction.commit()

            # full-page notification
            return message(req,
                "SMS notification %s added" % (notification.pk),
                link="/smsnotification")

        except Exception, err:
            transaction.rollback()
            raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)


@login_and_domain_required
def edit_notifications(req, pk):
    notification = get_object_or_404(SmsNotification, pk=pk)

    def get(req):
        template_name = "sms-notifications.html"
        notifications = SmsNotification.objects.all()
        districts = WqmAuthority.objects.all()
        points = SamplingPoint.objects.all()
        testers = get_tester(req.user)
        return render_to_response(req,
            template_name, {
                # display paginated sampling points
                "notifications": paginated(req, notifications, prefix="smsnotice"),
                "points" : points,
                "districts" : districts,
                "testers" : testers,
                "notification_types_choices" : NotificationChoice.objects.all(),
                "notification" : notification,
                })

    @transaction.commit_manually
    def post(req):
        # delete notification if a delete button was pressed.
        if req.POST.get("delete", ""):
            pk = notification.pk
            notification.delete()

            transaction.commit()
            return message(req,
                "Notification %d deleted" % (pk),
                link="/smsnotification")
        else:
            # check the form for errors
            notice_errors = check_notice_form(req)

            # if any fields were missing, abort.
            missing = notice_errors["missing"]
            exists = notice_errors["exists"]

            if missing:
                transaction.rollback()
                return message(req,
                    "Missing Field(s): %s" % comma(missing),
                    link="/smsnotification/add")
            # if authorised tester with same notification and point exists, abort.
    #        if exists:
    #            transaction.rollback()
    #            return message(req,
    #                "%s already exist" % comma(exists),
    #                link="/smsnotification/add")

            try:
                # create the notification object from the form
                rep = Reporter.objects.get(pk = req.POST.get("authorised_sampler",""))
                notification.authorised_sampler = rep

                choice = NotificationChoice.objects.get(pk = req.POST.get("notification_type",""))
                notification.notification_type = choice

                point = SamplingPoint.objects.get(pk = req.POST.get("sampling_point",""))
                notification.sampling_point = point

                notification.digest = req.POST.get("digest","")


                # save the changes to the db
                notification.save()
                transaction.commit()

                # full-page notification
                return message(req,
                    "SMS notification %s updated" % (notification.pk),
                    link="/smsnotification")

            except Exception, err:
                transaction.rollback()
                raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)

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