# Create your views here.

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cee1.settings import VERSION_STAMP
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

from session import AppUser

@ensure_csrf_cookie
def home(request):
    logger.info('Home')
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('home.html', context)

def narrow_network(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('narrow_network.html', context)

def cost_pharm(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('cost_pharm.html', context)

def pop_biom(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('pop_biom.html', context)

def pop_risk(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('pop_risk.html', context)

def notyet(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    messages.add_message(request, messages.ERROR, 'Not implemented yet')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('home.html', context)

def notfound(request):
    try:
        app_user = AppUser.get_by_username(request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        return redirect('/signout/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('404.html', context)

import cee1.rpc as rpc

class RPCMethods:
    def add(self, one, two):
        logger.info('one %s, two %s', one, two)
        return one+two

def RPCHandler(request):
    logger.info('home.views.RPCHandler')
    mObj = RPCMethods()
    return rpc.RPCHandler(request, mObj)
