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

def home(request):
    return  render_to_response('home.html', {}, context_instance=RequestContext(request) )

def notyet(request):
    messages.add_message(request, messages.ERROR, 'Not implemented yet')
    return  render_to_response('home.html', {}, context_instance=RequestContext(request) )
