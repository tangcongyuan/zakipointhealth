# Create your views here.

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pymongo import MongoClient

from zphalfa.settings import VERSION_STAMP, DATABASES
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

from session import AppUser
hm_users = ['j.singh@hsirx.com', 'yanpu@hsirx.com', 'eric@hsirx.com', 'heather@hsirx.com']
hm_data_users = ['j.singh@hsirx.com', 'yanpu@hsirx.com', 'eric@hsirx.com', 'heather@hsirx.com']

@ensure_csrf_cookie
def home(request):
    logger.info('Home')
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    hm_flag = True if request.session['username'] in hm_users else False
    hm_data = True if request.session['username'] in hm_data_users else False
    context = {'session': request.session, 'path': request.path, 'version': VERSION_STAMP,
               'fullname': fullname, 'hm_flag': hm_flag, 'hm_data': hm_data, }
    logger.info('home.html context %s', context)
    return  render_to_response('home.html', context)

def narrow_network(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('narrow_network.html', context)

def cost_pharm(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('cost_pharm.html', context)

def pop_biom(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logout works whether someone is signed in or not. session wiped.
        return redirect('/')

    hm_flag = True if request.session['username'] in hm_users else False
    hm_data = True if request.session['username'] in hm_data_users else False
    context = {'session': request.session, 'path': request.path, 'version': VERSION_STAMP,
               'fullname': fullname, 'hm_flag': hm_flag, 'hm_data': hm_data, }
    return  render_to_response('pop_biom.html', context)

def pop_risk(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('pop_risk.html', context)

def notyet(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    messages.add_message(request, messages.ERROR, 'Not implemented yet')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('home.html', context)

def notfound(request):
    try:
        app_user = AppUser.find(username = request.session['username'])
        fullname = app_user.get_full_name()
    except (IndexError, KeyError):
        logout(request)  # logut works whether someone is signed in or not. session wiped.
        return redirect('/')
    context = {'session': request.session, 'path': request.path, 'fullname': fullname, 'version': VERSION_STAMP}
    return  render_to_response('404.html', context)

import zphalfa.rpc as rpc

class RPCMethods:
    def add(self, one, two):
        logger.info('one %s, two %s', one, two)
        return one+two
    def eligible(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['biometrics']

        #eligible members for each year
        pipeline1 = [
            {"$group": {"_id": "$Year", "count": {"$sum": 1}}}
        ]
        answer = list(collection.aggregate(pipeline1))
        logger.info("eligible member in each year: %s", answer)
        return answer
    def participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['biometrics']
        pipeline2 = [
            {
                "$group":
                {
                    "_id":{"Year":"$Year","Status":"$HRAStat"},
                    "count":{"$sum":1}
                }
            }
        ]
        answer = list(collection.aggregate(pipeline2))
        logger.info("participating members in each year: %s", answer)
        return answer

    def members_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        Year=["12","13","14"]
        answer = {}
        for y in Year:
            resultMembers = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$group":{"_id":"%s"%(y), "Num of Member":{"$sum":1}}}
            ])
            answer[y] = list(resultMembers)
        logger.info('Number of Participating Members by year, %s', answer)
        return answer

    def expenses_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #expenses for each year
        Year=["12","13","14"]
        answer = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer[y] = list(resultFees)
        logger.info('Expenses of Participating Members by year, %s', answer)
        return answer

    def members_non_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        Year=["12","13","14", "15"]
        partMember = {}
        for y in Year:
            partMember[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")

        answer = {}
        for y in Year:
            resultMembers = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "Num of Member":{"$sum":1}}}
            ])
            answer[y] = list(resultMembers)
        logger.info('All Members by year, %s', answer)
        return answer

    def expenses_non_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        Year=["12","13","14", "15"]
        partMember = {}
        for y in Year:
            partMember[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")

        answer = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer[y] = list(resultFees)
        logger.info('Participating Member Expenses by year, %s', answer)
        return answer

    def members_engaged(self):
#        answer = 'Engaged Member count by year not ready yet'
#        return answer
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance',
                            'GraduatetoRP','MedRxActive','GraduateRP','Monthly',
                            'movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
                       'N':['NotRequired','OptOut','Terminated','Missed',
                            'Dismissed','AppealFollowUp'],
        }
        engagedMember={}
        Year=["12","13","14", "15"]
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}    
                ]
             } ).distinct("UID")

        answer = {}
        for y in Year:
            resultMembers = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "Num of Member":{"$sum":1}}}
            ])
            answer[y] = list(resultMembers)
        logger.info('Engaged Members by year, %s', answer)
        return answer

    def expenses_engaged(self):
#        answer = 'Engaged Member Expenses by year not ready yet'
#        return answer
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance',
                            'GraduatetoRP','MedRxActive','GraduateRP','Monthly',
                            'movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
                       'N':['NotRequired','OptOut','Terminated','Missed',
                            'Dismissed','AppealFollowUp'],
        }
        engagedMember={}
        Year=["12","13","14", "15"]
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}    
                ]
             } ).distinct("UID")

        answer = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer[y] = list(resultFees)
        logger.info('Engaged Members by year, %s', answer)
        return answer

def RPCHandler(request):
    logger.info('home.views.RPCHandler')
    mObj = RPCMethods()
    return rpc.RPCHandler(request, mObj)
