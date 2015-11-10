# Create your views here.

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import time

from pymongo import MongoClient

from zphalfa.settings import VERSION_STAMP, DATABASES
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)


import zphalfa.rpc as rpc

EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance',
                    'GraduatetoRP','MedRxActive','GraduateRP','Monthly',
                    'movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed',
                    'Dismissed','AppealFollowUp']}

RiskMap = {
    "RiskReduction": "Med",
    "RiskPrevention": "Low",
    "ChronicCare": "High",
}

class RPCMethods:
    def eligible(self):
        t0 = time.time()
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
        logger.info("%.2f eligible member in each year: %s", time.time() - t0, answer)
        return answer

    def participating(self):
        t0 = time.time()
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
        
        logger.info("%.2f participating members in each year: %s", time.time() - t0, answer)
        return answer

    def engaged(self):
        t0 = time.time()
        #engaged members
#        answer = [{"count": 146, "_id": "2012"}, {"count": 383, "_id": "2013"}, {"count": 413, "_id": "2014"}, {"count": 449, "_id": "2015"}]
        answer = [{"count": 146, "_id": "2012"}, {"count": 413, "_id": "2014"}, {"count": 449, "_id": "2015"}]
        return answer
        result=collection.aggregate([
            {"$match": {"Msubs": {"$in":EngagedStatus['Y']}}},
            { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
        ])
        logger.info('%.2f engaged %s', time.time() - t0, result)
        return result

    def members_participating(self):
        t0 = time.time()
        answer_dict = self.members_participating_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_participating_raw(self):
        t0 = time.time()
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
        logger.info('%.2f All Members by year, %s', time.time() - t0, answer_dict)
        return answer_dict

    def expenses_participating(self):
        t0 = time.time()
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
        
        logger.info('%.2f Participating Member Expenses by year, %s', time.time() - t0, answer)
        return answer

    def members_non_participating(self):
        answer_dict = self.members_non_participating_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_non_participating_raw(self):
        t0 = time.time()
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
        logger.info('%.2f All Members by year, %s', time.time() - t0, answer)
        return answer

    def expenses_non_participating(self):
        t0 = time.time()
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
        
        logger.info('%.2f Non-Participating Member Expenses by year, %s', time.time() - t0, answer)
        return answer

    def members_engaged(self):
        answer_dict = self.members_engaged_raw()
        # {"13": 258, "12": 398, "15": 0, "14": 706}
        # [{"count": 434, "_id": "2012"}, {"cou...  ]
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_engaged_raw(self):
        t0 = time.time()
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
        logger.info('%.2f Engaged Members by year, %s', time.time() - t0, answer)
        return answer

    def expenses_engaged(self):
        t0 = time.time()
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
        
        logger.info('%.2f Engaged Expenses by year, %s', time.time() - t0, answer)
        return answer

    def figure_3(self):
        #########Figure 3
        t0 = time.time()
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
            total = lt500[y] + between[y] + gt10k[y]
            lo_spenders = round(lt500[y]*100.0/total)
            hi_spenders = round(gt10k[y]*100.0/total)
            ret.append({
                "Year": "20"+y,
                "under_500": int(lo_spenders),
                "between": int(100 - lo_spenders - hi_spenders),
                "over_10k": int(hi_spenders),
            })
        logging.info('%.2f figure_3 returns %s', time.time() - t0, ret)
        return ret

    def non_participant_claims(self):
        t0 = time.time()
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
            total = lt500[y] + between[y] + gt10k[y]
            lo_spenders = round(lt500[y]*100.0/total)
            hi_spenders = round(gt10k[y]*100.0/total)
            ret.append({
                "Year": "20"+y,
                "under_500": int(lo_spenders),
                "between": int(100 - lo_spenders - hi_spenders),
                "over_10k": int(hi_spenders),
            })
        logging.info('%.2f non_participant_claims returns %s', time.time() - t0, ret)
        return ret

    def participant_claims (self):
        t0 = time.time()
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
            total = lt500[y] + between[y] + gt10k[y]
            lo_spenders = round(lt500[y]*100.0/total)
            hi_spenders = round(gt10k[y]*100.0/total)
            ret.append({
                "Year": "20"+y,
                "under_500": int(lo_spenders),
                "between": int(100 - lo_spenders - hi_spenders),
                "over_10k": int(hi_spenders),
            })
        logging.info('%.2f participant_claims returns %s', time.time() - t0, ret)
        return ret

    def engaged_claims(self):
        t0 = time.time()
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
            total = lt500[y] + between[y] + gt10k[y]
            lo_spenders = round(lt500[y]*100.0/total)
            hi_spenders = round(gt10k[y]*100.0/total)
            ret.append({
                "Year": "20"+y,
                "under_500": int(lo_spenders),
                "between": int(100 - lo_spenders - hi_spenders),
                "over_10k": int(hi_spenders),
            })
        logging.info('%.2f engaged_claims returns %s', time.time() - t0, ret)
        return ret

    def risk_participating(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        level=RiskMap.keys()
        answer_dict_list = []
        answer_dict = {}
        for l in level:
            result=db.biometrics.aggregate([
                {"$match": {"Mstat": l}},
                { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
            ])
            answer_dict_list.append(l)
            for item in result:
                answer_dict_list.append(item)
            answer_dict[RiskMap[l]] = list(result)
        answer = []

        for i in range(len(answer_dict_list)):
            ans1={}
            if(i<4):
                ans1["Year"]="20"+str(answer_dict_list[i+1]['_id'])
                total=float(answer_dict_list[i+ 1]['count']+answer_dict_list[i+ 6]['count']+answer_dict_list[i+11]['count'])
                ans1[RiskMap[answer_dict_list[ 0]]]=int(round(answer_dict_list[i+ 1]['count']/total*100, 0))
                ans1[RiskMap[answer_dict_list[ 5]]]=int(100-round(answer_dict_list[i+ 1]['count']/total*100, 0)-round(answer_dict_list[i+11]['count']/total*100, 0))
                ans1[RiskMap[answer_dict_list[10]]]=int(round(answer_dict_list[i+11]['count']/total*100, 0))
            else: 
                break
            answer.append(ans1)
        logger.info('%.2f risk_participating returning %s', time.time()-t0, answer)
        return answer

    def risk_engaged(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        Year=["12","13","14", "15"]
        answer_dict_list = []
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

        answer = []

        level=RiskMap.keys()
        for l in level:
            result=db.biometrics.aggregate([
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match": {"Mstat": l}},
                { "$group": {"_id": "$Year", "count": {"$sum": 1}}}
            ])
            answer_dict_list.append(l)
            for item in result:
                answer_dict_list.append(item)
        for i in range(len(answer_dict_list)):
            ans1={}
            if(i<4):
                ans1["Year"]="20"+str(answer_dict_list[i+1]['_id'])
                total=float(answer_dict_list[i+ 1]['count']+answer_dict_list[i+ 6]['count']+answer_dict_list[i+11]['count'])
                ans1[RiskMap[answer_dict_list[ 0]]]=int(round(answer_dict_list[i+ 1]['count']/total*100, 0))
                ans1[RiskMap[answer_dict_list[ 5]]]=int(100-round(answer_dict_list[i+ 1]['count']/total*100, 0)-round(answer_dict_list[i+11]['count']/total*100, 0))
                ans1[RiskMap[answer_dict_list[10]]]=int(round(answer_dict_list[i+11]['count']/total*100, 0))
            else: 
                break
            answer.append(ans1)
        logger.info('%.2f risk_engaged answer: %s', time.time() - t0, answer)
        return answer

    def risk_participating_changes(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        '''
        chronicCare: high
        riskReduction: medium
        riskPrevention: low
        '''
        print "high:chronicCare"
        print "medium:riskReduction"
        print "low:riskPrevention"
        level=["RiskPrevention","RiskReduction","ChronicCare"]
        Year=['12','13','14','15']
        period=['12-13','13-14','14-15']
        groupHigh = {}
        groupMe = {}
        groupLow = {}
        interResult = {}
        finalResult = []
        for l in level:
            result=db.bio.aggregate([
                {"$match": {"Mstat": l}}, 
                { "$group": {"_id": {"Year":"$Year","UID":"$UID","Risk":"$Mstat"}}}
            ])
    
            i=0
            for document in result:   
                for y in Year:
                    if (document["_id"]["Year"]==int(y)): 
                        interResult.setdefault(y,[]).append(document['_id']['UID'])
        for y in Year:
            if(l=="ChronicCare"):
                groupHigh[y]=interResult[y]
            elif(l=="RiskReduction"):
                groupMe[y]=interResult[y]
            else:
                groupLow[y]=interResult[y]
        interResult={}
        # corresponding level mapping, like high to high
        for item in period:
            print "period %s:"%item
            print "corresponding level mapping, like high to high:"
            print "[high, medium, low]"
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
            print len(set(groupMe[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupLow[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            # Uncorresponding level mapping, like high to medium
            print
            print "[high to me, high to low]"
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            print "[medium to low, medium to high]"
            print len(set(groupMe[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            print len(set(groupMe[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
            print "[low to me, low to high]"
            print len(set(groupLow[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupLow[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
        return answer

    def risk_engaged_changes(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        #Graph Risk Engaged
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
                       'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        level=["RiskPrevention","RiskReduction","ChronicCare"]
        Year=['12','13','14','15']
        period=['12-13','13-14','14-15']
        groupHigh = {}
        groupMe = {}
        groupLow = {}
        interResult = {}
        finalResult = []
        engagedMember={}


        for y in Year:
            engagedMember[y]=db.bio.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
             } ).distinct("UID")
        for l in level:
            result=db.bio.aggregate([
                {"$match": {"Mstat": l}}, 
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},

                { "$group": {"_id": {"Year":"$Year","UID":"$UID","Risk":"$Mstat"}}}
            ])
    
        i=0
        for document in result:   
            for y in Year:
                if (document["_id"]["Year"]==int(y)): 
                    interResult.setdefault(y,[]).append(document['_id']['UID'])
            for y in Year:
                if(l=="ChronicCare"):
                    groupHigh[y]=interResult[y]
                
                elif(l=="RiskReduction"):
                    groupMe[y]=interResult[y]
                
                else:
                    groupLow[y]=interResult[y]
        interResult={}
        # corresponding level mapping, like high to high
        for item in period:
            print "period %s:"%item
            print "corresponding level mapping, like high to high:"
            print "[high, medium, low]"
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
            print len(set(groupMe[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupLow[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            # Uncorresponding level mapping, like high to medium
            print
            print "[high to me, high to low]"
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupHigh[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            print "[medium to low, medium to high]"
            print len(set(groupMe[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
            print len(set(groupMe[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
            print "[low to me, low to high]"
            print len(set(groupLow[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
            print len(set(groupLow[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
        return answer

def RPCHandler(request):
    logger.info('home.healthmetrics.RPCHandler')
    mObj = RPCMethods()
    return rpc.RPCHandler(request, mObj)
