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
from wqm.models import WqmAuthority
from samples.models import Sample

logger_set = False


@login_and_domain_required
def samples(req):
    template_name = 'samples.html'
    testers = get_tester(req.user)
    districts = WqmAuthority.objects.all()

    
    query = Sample.objects.filter(taken_by__in=testers)
    search_string = req.REQUEST.get("q", "")
    if search_string == "":
        query = query.filter(sampling_point__wqmarea__wqmauthority__in = districts)
    else:
        query = query.filter(sampling_point__wqmarea__wqmauthority__in = search_string)
        search_string = WqmAuthority.objects.filter(id = search_string) 
    return render_to_response(req, template_name,
                              { 
                              "sort_districts" : districts,
                              "districts" : districts,
                              "samples": paginated(req, query),
                              "search_string" : search_string,
                              })

def get_tester(user):
    # todo: get the testers in the system with the same
    # domain as the login user.
    rep_profile = ReporterProfile.objects.filter(domain=user.selected_domain)
    reporters = []

    if rep_profile:
        for rep in rep_profile:
            reporter = rep.reporter
            reporters.append(reporter)
    return reporters