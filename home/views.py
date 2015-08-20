# Create your views here.

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

from session import AppUser

def home(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except IndexError:
        fullname = ''
    return  render_to_response('home.html', {'session': request.session, 'fullname': fullname} )

def narrow_network(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except IndexError:
        fullname = ''
    return  render_to_response('narrow_network.html', {'session': request.session, 'fullname': fullname} )

def pharm_cost(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except IndexError:
        fullname = ''
    return  render_to_response('pharm_cost.html', {'session': request.session, 'fullname': fullname} )

def notyet(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except IndexError:
        fullname = ''
    messages.add_message(request, messages.ERROR, 'Not implemented yet')
    return  render_to_response('home.html', {'session': request.session, 'fullname': fullname} )