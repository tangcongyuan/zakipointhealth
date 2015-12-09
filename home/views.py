# Create your views here.

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.models import Site

import sys, time

from pymongo import MongoClient

from zphalfa.settings import VERSION_STAMP, DATABASES, ga_codes

import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

from models import AppUser
from session import capability_required, request_passes_test

def user_context(request):
    try:
        username = request.session['username']
        channel_logo = request.session['channel_logo']
        company_logo = request.session['company_logo']
        app_user = AppUser.get(username)
        fullname = app_user.user.get_full_name()
        site = Site.objects.get_current()

    except KeyError:
        channel_logo = "/static/images/logo-blue-transparent.png"
        company_logo = "/static/dimages/tilde.png"
        fullname = ''
        site = Site.objects.get()

    try:
        ga_code = ga_codes[site.name]
    except KeyError:
        ga_code = ga_codes['default']

    context = {
        'session': request.session, 
        'path': request.path, 
        'version': VERSION_STAMP,
        'fullname': fullname, 
        'channel_logo': channel_logo,
        'company_logo': company_logo,
        'site': site.name,
        'ga_code': ga_code,
    }
    callingframe = sys._getframe(1)
    logger.info( '\n----\n%r context %s\n--------', callingframe.f_code.co_name, context)
    return context

@request_passes_test(lambda rqst: capability_required(rqst, "home"))
@login_required
def home(request):
    # This construct derives the name of the html file from the name of the function
    # sys._getframe(0).f_code.co_name returns the name of this function
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def narrow_network(request):
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def cost_pharm(request):
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def monthly_cost(request):
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def pop_biom(request):
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def pop_risk(request):
    return render_to_response(sys._getframe(0).f_code.co_name+'.html', user_context(request))

@login_required
def notyet(request):
    messages.add_message(request, messages.ERROR, 'Not implemented yet')
    return  render_to_response('home.html', user_context(request))

@login_required
def notfound(request):
    return  render_to_response('404.html', user_context(request))
