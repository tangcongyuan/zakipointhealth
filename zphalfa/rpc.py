from bson import json_util
import sys, json, datetime
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

class RPCMethods:
    pass

def RPCHandler(request, mObj = RPCMethods()):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    # logger.info('In RPCHandler, user %s, co %s', request.session['username'], request.session['user_co'])
    if request.method == 'POST':
        post_data = request.POST
        func = request.POST.get('func', None)
        if not func:
            logger.error("Forbidden: func not provided") 
            return HttpResponseForbidden()
        
        if func[0] == '_':
            logger.error("%s is a protected function",func) 
            return HttpResponseForbidden()

        func = getattr(mObj, func, None)

        if not func:
            logger.error("RPC func Not found %s",func) 
            return HttpResponseNotFound()
    
        #logger.info('RPCHandler %s()', func)
        args = request.POST.get('args')
        args = json.loads(args)
        #logger.info('RPCHandler %s(%s)', func, args)
        try:
            result = func(*args)
            # http://stackoverflow.com/questions/8409194/unable-to-deserialize-pymongo-objectid-from-json
            return HttpResponse(json.dumps(result, default=json_util.default))
            # return HttpResponse(json.dumps(result), mimetype="application/json")
        except Exception as inst:
            logger.error('Failed %s', str(inst))
            return HttpResponseServerError()
    else:
        # All other conditions should be refused
        return HttpResponseNotAllowed(['POST'])
