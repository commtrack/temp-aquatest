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

from rapidsms.webui.utils import render_to_response, paginated

from domain.decorators import login_and_domain_required
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

from reporters.utils import *
from reporters.views import message, check_reporter_form, update_reporter
#from reporters.models import Reporter, PersistantBackend, PersistantConnection
from reporters.models import *

logger_set = False


from reporters.utils import *


def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })

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
def index(req):
    query = ReporterProfile.objects.filter(domain=req.user.selected_domain).order_by('reporter__first_name')
    search_string = req.REQUEST.get("q", "")
    if search_string == "":
        pass
    else:
        query = query.filter(
           Q(reporter__first_name__icontains = search_string ) |
           Q(reporter__last_name__icontains = search_string))
    
    reporters = []
    for rep in query:
        reporter = rep.reporter
        reporters.append(reporter)
    
    return render_to_response(req,
        "testers/index.html", {
        "reporters": paginated(req, reporters, prefix="rep"),
        "groups":    paginated(req, ReporterGroup.objects.flatten(), prefix="grp"),
        "search_string" : search_string,
    })


def check_reporter_form(req):

    # verify that all non-blank
    # fields were provided
    missing = [
        field.verbose_name
        for field in Reporter._meta.fields
        if req.POST.get(field.name, "") == ""
           and field.blank == False]

    exists = []
    alias = req.POST.get("alias","")
    if Reporter.objects.filter( alias=alias ):
        exists = ['alias']

    # TODO: add other validation checks,
    # or integrate proper django forms
    return {
        "missing": missing,
        "exists": exists }

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def add_testers(req):
    # NOTE/TODO:
    # this is largely a copy paste job from rapidsms/apps/reporters/views.py
    # method of the same name, and really doesn't belong here at all.

    def get(req):
        # pre-populate the "connections" field
        # with a connection object to convert into a
        # reporter, if provided in the query string
        connections = []
        if "connection" in req.GET:
            connections.append(
                get_object_or_404(
                    PersistantConnection,
                    pk=req.GET["connection"]))

        reporters = get_tester(req.user)
        return render_to_response(req,
            "testers/testers.html", {

                # display paginated reporters in the left panel
                "reporters": paginated(req, reporters),

                # pre-populate connections
                "connections": connections,

                # list all groups + backends in the edit form
                "all_groups": ReporterGroup.objects.flatten(),
                "all_backends": PersistantBackend.objects.all() })

    @transaction.commit_manually
    def post(req):
        # check the form for errors
        reporter_errors = check_reporter_form(req)
        profile_errors = check_profile_form(req)

        # if any fields were missing, abort.
        missing = reporter_errors["missing"] + profile_errors["missing"]
        exists = reporter_errors["exists"] + profile_errors["exists"]

        if missing:
            transaction.rollback()
            return message(req,
                "Missing Field(s): %s" % comma(missing),
                link="/testers/add")
        # if chw_id exists, abort.
        if exists:
            transaction.rollback()
            return message(req,
                "Field(s) already exist: %s" % comma(exists),
                link="/testers/add")

        try:
            # create the reporter object from the form
            rep = insert_via_querydict(Reporter, req.POST)
            rep.save()

            # add relevent connections
            update_reporter(req, rep)
            # create reporter profile
            update_reporterprofile(req, rep, req.POST.get("chw_id", ""), \
                                   req.POST.get("alias", ""), \
                                   req.POST.get("e_mail", ""))
            # save the changes to the db
            transaction.commit()

            # full-page notification
            return message(req,
                "Testers %d added" % (rep.pk),
                link="/testers")

        except Exception, err:
            transaction.rollback()
            raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)



@require_http_methods(["GET", "POST"])
@login_and_domain_required
def edit_testers(req, pk):
    rep = get_object_or_404(Reporter, pk=pk)
    rep_profile = get_object_or_404(ReporterProfile, reporter=rep)
    rep.chw_id = rep_profile.chw_id
    rep.chw_username = rep_profile.chw_username
    rep.e_mail = rep_profile.e_mail

    def get(req):
        return render_to_response(req,
            "testers/testers.html", {

                # display paginated reporters in the left panel
                "reporters": paginated(req, Reporter.objects.all()),

                # list all groups + backends in the edit form
                "all_groups": ReporterGroup.objects.flatten(),
                "all_backends": PersistantBackend.objects.all(),

                # split objects linked to the editing reporter into
                # their own vars, to avoid coding in the template
                "connections": rep.connections.all(),
                "groups":      rep.groups.all(),
                "reporter":    rep })

    @transaction.commit_manually
    def post(req):

        # if DELETE was clicked... delete
        # the object, then and redirect
        if req.POST.get("delete", ""):
            pk = rep.pk
            rep_profile.delete()
            rep.delete()

            transaction.commit()
            return message(req,
                "Tester %d deleted" % (pk),
                link="/testers")

        else:
            # check the form for errors (just
            # missing fields, for the time being)
            reporter_errors = check_reporter_form(req)
            profile_errors = check_profile_form(req)

            # if any fields were missing, abort. this is
            # the only server-side check we're doing, for
            # now, since we're not using django forms here
            missing = reporter_errors["missing"] + profile_errors["missing"]
            if missing:
                transaction.rollback()
                return message(req,
                    "Missing Field(s): %s" %
                        ", ".join(missing),
                    link="/testers/%s" % (rep.pk))

            try:
                # automagically update the fields of the
                # reporter object, from the form
                update_via_querydict(rep, req.POST).save()
                # add relevent connections
                update_reporter(req, rep)
                # update reporter profile
                update_reporterprofile(req, rep, req.POST.get("chw_id", ""), \
                                       req.POST.get("chw_username", ""), \
                                       req.POST.get("e_mail", ""))

                # no exceptions, so no problems
                # commit everything to the db
                transaction.commit()

                # full-page notification
                return message(req,
                    "Tester %d updated" % (rep.pk),
                    link="/testers")

            except Exception, err:
                transaction.rollback()
                raise

    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)

@require_http_methods(["GET", "POST"])
@login_and_domain_required
def delete_testers(req, pk):
    rep = get_object_or_404(Reporter, pk=pk)
    rep_profile = get_object_or_404(ReporterProfile, reporter=rep)
    rep_profile.delete()
    rep.delete()

    transaction.commit()
    id = int(pk)
    return message(req,
        "Tester %d deleted" % (id),
        link="/testers")


def update_reporterprofile(req, rep, chw_id, chw_username, e_mail):
    try:
        profile = ReporterProfile.objects.get(reporter=rep)
    except ReporterProfile.DoesNotExist:
        profile = ReporterProfile(reporter=rep, approved=True, active=True, \
                                  guid = str(uuid.uuid1()).replace('-',''))
        # reporters created through the webui automatically have the same
        # domain and organization as the creator
        profile.domain = req.user.selected_domain
    profile.chw_id = chw_id
    profile.chw_username = chw_username
    profile.e_mail = e_mail
    profile.save()

def check_profile_form(req):
    errors = {}
    errors['missing'] = []
    # we currently do not enforce the requirement for chw_id or chw_username
    #if req.POST.get("chw_id", "") == "":
    #    errors['missing'] = errors['missing'] + ["chw_id"]
    #if req.POST.get("chw_username", "") == "":
    #    errors['missing'] = errors['missing'] + ["chw_username"]

    errors['exists'] = []
    chw_id = req.POST.get("chw_id", "")
    if chw_id:
        # if chw_id is set, it must be unique for a given domain
        rps = ReporterProfile.objects.filter(chw_id=req.POST.get("chw_id", ""), domain=req.user.selected_domain)
        if rps: errors['exists'] = ["chw_id"]
    return errors

def comma(string_or_list):
    """ TODO - this could probably go in some sort of global util file """
    if isinstance(string_or_list, basestring):
        string = string_or_list
        return string
    else:
        list = string_or_list
        return ", ".join(list)

