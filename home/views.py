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
hm_data_users = []#['j.singh@hsirx.com', 'yanpu@hsirx.com', 'eric@hsirx.com']

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

EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance',
                    'GraduatetoRP','MedRxActive','GraduateRP','Monthly',
                    'movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed',
                    'Dismissed','AppealFollowUp']}

class RPCMethods:
    def add(self, one, two):
        logger.info('one %s, two %s', one, two)
        return one+two

    def eligible(self):
        Year=["2012","2014","2015"]
        answer = [{"_id": yr, "count": 1309} for yr in Year]
        return answer

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
        answer_dict = list(collection.aggregate(pipeline2))
        # [{"count": 434, "_id": {"Status": "Primary", "Year": 12}}, {"count": 950, "_id": {"Status": "Primary", "Year": 14}},...]
        # [{"count": 1309, "_id": "12"}, {"count": 1309, "_id": "13"}, {"count": 1309, "_id": "14"}]
        answer = [{"count": v['count'], "_id":str(v['_id']['Year']+2000)} for v in answer_dict if v['_id']['Year'] != 13]
        
        logger.info("participating members in each year: %s", answer)
        return answer

    def engaged(self):
        #engaged members
#        answer = [{"count": 146, "_id": "2012"}, {"count": 383, "_id": "2013"}, {"count": 413, "_id": "2014"}, {"count": 449, "_id": "2015"}]
        answer = [{"count": 146, "_id": "2012"}, {"count": 413, "_id": "2014"}, {"count": 449, "_id": "2015"}]
        return answer
        result=collection.aggregate([
            {"$match": {"Msubs": {"$in":EngagedStatus['Y']}}},
            { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
        ])
        logger.info('engaged %s', result)
        return result

    def members_participating(self):
        answer_dict = self.members_participating_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_participating_raw(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        Year=["12","14","15"]
        partMember = {}
        for y in Year:
            partMember[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")

        answer_dict = {}
        for y in Year:
            resultMembers = collection.aggregate([
                {"$match":{"Year": y}},
                # {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "Num of Member":{"$sum":1}}}
            ])
            answer_dict[y] = len(list(resultMembers))
        logger.info('All Members by year, %s', answer_dict)
        return answer_dict

    def expenses_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #expenses for each year
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        partMember = {}
        for y in Year:
            partMember[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")

        answer_dict = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"Year": y}},
                # {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer_dict[y] = list(resultFees)
        # {"13": [{"TotalPaid": 197142.51000000024, "_id": "13"}], "12": [{"TotalPaid": 1754748.4399999501, "_id": "12"}], "15": [], "14": [{"TotalPaid": 3112128.1199999745, "_id": "14"}]}

        members = self.members_participating_raw()
        logger.info('self.members_participating_raw: %s', members)
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('Participating Member Expenses by year, %s', answer)
        return answer

    def members_non_participating(self):
        answer_dict = self.members_non_participating_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_non_participating_raw(self):
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
                {"$match":{"Year": y}},
                # {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "Num of Member":{"$sum":1}}}
            ])
            answer[y] = len(list(resultMembers))
        logger.info('All Members by year, %s', answer)
        return answer

    def expenses_non_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #members for each year
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        partMember = {}
        for y in Year:
            partMember[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")

        answer_dict = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"Year": y}},
                # {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer_dict[y] = list(resultFees)
        members = self.members_non_participating_raw()
        logger.info('self.members_non_participating_raw: %s', members)
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('Non-Participating Member Expenses by year, %s', answer)
        return answer

    def members_engaged(self):
        answer_dict = self.members_engaged_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_engaged_raw(self):
#        answer = 'Engaged Member count by year not ready yet'
#        return answer
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        engagedMember={}
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
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
                {"$match":{"Year":y}},
                #{"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "Num of Member":{"$sum":1}}}
            ])
            answer[y] = len(list(resultMembers))
        logger.info('Engaged Members by year, %s', answer)
        return answer

    def expenses_engaged(self):
#        answer = 'Engaged Member Expenses by year not ready yet'
#        return answer
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #memmbers for each year
        engagedMember={}
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
             } ).distinct("UID")

        answer_dict = {}
        for y in Year:
            resultFees = collection.aggregate([
                {"$match":{"Year":y}},
                #{"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
            ])
            answer_dict[y] = list(resultFees)
        members = self.members_engaged_raw()
        logger.info('self.members_engaged: %s', members)
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('Engaged Expenses by year, %s', answer)
        return answer

    def figure_3(self):
        #########Figure 3
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        claims = db['claims']
        logger.info('In figure 3')

        partMember = {}
        Year=["12","13","14", "15"]
        Year=["12","14"]
        for y in Year:
            partMember[y] = list(db.biometrics.find({"Year":int(y)}).distinct("UID"))
        #logger.info('partMember %s', partMember)

        lt500 = {}
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":500}}}
            ])
            lt500[y] = len(list(resultFees))
            logger.info("{Year: %s, Num of Members < 500: %s}"%(y,len(list(resultFees))))

        between = {}
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":10000,"$gt":500}}}
            ])
            between[y] = len(list(resultFees))
            logger.info("{Year: %s, Num of Members in [500,10000]: %s}"%(y,len(list(resultFees))))

        gt10k = {}
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$gt":10000}}}
            ])
            gt10k[y] = len(list(resultFees))
            logger.info("{Year: %s, Num of Members > 10000: %s}"%(y,len(list(resultFees))))
            # [{"12": 86, "14": 189}, {"12": 269, "14": 462}, {"12": 43, "14": 60}]
        ret = []
        for y in Year:
            ret.append({
                "Year": "20"+y,
                "under_500": lt500[y],
                "between": between[y],
                "over_10k": gt10k[y],
            })
        logging.info('figure_3 returns %s', ret)
        return ret

    def risk_participating(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        level=["RiskPrevention","RiskReduction","ChronicCare"]
        answer = {}
        for l in level:
            result=db.biometrics.aggregate([
                {"$match": {"Mstat": l}},
                { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
            ])
            answer[l] = list(result)
            logger.info( "For %s level members:", l, answer[l])
        return answer

    def risk_engaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        Year=["12","13","14", "15"]

        engCount = {}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
             } ).distinct("UID")
            engCount[y] = len(engagedMember[y])
        logger.info('risk_engaged Engaged risk counts %s', engCount)

        answer = {}

        level=["RiskPrevention","RiskReduction","ChronicCare"]
        for l in level:
            result=db.biometrics.aggregate([
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match": {"Mstat": l}},
                { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
            ])
            answer[l] = list(result)
        logger.info('risk_engaged answer: %s', answer)
        return answer

    def non_participant_claims(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        claims = db['claims']
        logger.info( "non-participating Member:")
        partMember = {}
        Year=["12","13","14", "15"]
        Year=["12","14"]
        for y in Year:
            partMember[y] = list(db.biometrics.find({"Year":int(y)}).distinct("UID"))
        logger.info( "Range <= 500:")

        lt500 = {}
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":500}}}
            ])
            lt500[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members < 500: %s}"%(y,lt500[y]))

        between = {}
        logger.info( "Range [500,10000]:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":10000,"$gt":500}}}
            ])
            between[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members in [500,10000]: %s}"%(y,len(list(resultFees))))

        gt10k = {}
        logger.info( "Range >= 10000:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$nin":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$gt":10000}}}
            ])
            gt10k[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members > 10000: %s}"%(y,len(list(resultFees))))
        ret = []
        for y in Year:
            ret.append({
                "Year": "20"+y,
                "under_500": lt500[y],
                "between": between[y],
                "over_10k": gt10k[y],
            })
        logging.info('non_participant_claims returns %s', ret)
        return ret

    def participant_claims (self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        claims = db.claims
        logger.info( "participating Member:")
        partMember = {}
        Year=["12","13","14", "15"]
        Year=["12","14"]
        for y in Year:
            partMember[y] = list(db.biometrics.find({"Year":int(y)}).distinct("UID"))

        logger.info( "Range <= 500:")
        answer = {}
        lt500 = {}
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":500}}}
            ])
            lt500[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members below 500: %s}"%(y,lt500[y]))

        between = {}
        logger.info( "Range [500,10000]:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":10000,"$gt":500}}}
            ])
            between[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members in [500,10000]: %s}"%(y,between[y]))

        gt10k = {}
        logger.info( "Range >= 10000:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":partMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$gt":10000}}}
            ])
            gt10k[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members above 10000: %s}"%(y,gt10k[y]))
        ret = []
        for y in Year:
            ret.append({
                "Year": "20"+y,
                "under_500": lt500[y],
                "between": between[y],
                "over_10k": gt10k[y],
            })
        logging.info('participant_claims returns %s', ret)
        return ret

    def engaged_claims(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        claims = db.claims
        logger.info( "engaged Member:")
        engagedMember={}
        Year=["12","13","14", "15"]
        Year=["12","14"]

        for y in Year:
            engagedMember[y]=list(db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
             } ).distinct("UID"))

        lt500 = {}
        logger.info( "Range <= 500:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":500}}}
            ])
            lt500[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members below 500: %s}"%(y,lt500[y]))

        between = {}
        logger.info( "Range [500,10000]:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$lt":10000,"$gt":500}}}
            ])
            between[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members in [500,10000]: %s}"%(y,between[y]))

        gt10k = {}
        logger.info( "Range >= 10000:")
        for y in Year:
            resultFees = claims.aggregate([
                {"$match":{"Year":y}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
                {"$match":{"TotalPaid": {"$gt":10000}}}
            ])
            gt10k[y] = len(list(resultFees))
            logger.info( "{Year: %s, Num of Members above 10000: %s}"%(y,len(list(resultFees))))
        ret = []
        for y in Year:
            ret.append({
                "Year": "20"+y,
                "under_500": lt500[y],
                "between": between[y],
                "over_10k": gt10k[y],
            })
        logging.info('engaged_claims returns %s', ret)
        return ret

def RPCHandler(request):
    logger.info('home.views.RPCHandler')
    mObj = RPCMethods()
    return rpc.RPCHandler(request, mObj)
