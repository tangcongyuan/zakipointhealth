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

def participating_member_uids(db, Year):
    member_uids = {}
    for y in Year:
        member_uids[y] = db.biometrics.find({"Year":int(y)}).distinct("UID")
    logger.info('participating_member_uids %s', [{'y': y, 'count': len(member_uids[y])} for y in Year])
    return member_uids

def engaged_member_uids(db, Year):
    member_uids={}
    for y in Year:
        member_uids[y]=db.biometrics.find(
            {"$and":[
                {"Year":int(y)},
                {"Msubs": {"$in":EngagedStatus['Y']}}
            ]
         } ).distinct("UID")
    logger.info('engaged_member_uids %s', [{'y': y, 'count': len(member_uids[y])} for y in Year])
    return member_uids

def member_count(mongodb, member_uids, including=True):
    in_or_nin = '$in' if including else '$nin'
    logger.info('member_count %s', member_uids.keys())
    answer = {}
    for y in member_uids.keys():
        logger.info('loop begins %s, %s %s', in_or_nin, y, len(member_uids[y]))
        resultMembers = mongodb['claims'].aggregate([
            {"$match":{"Year":y}},
            {"$match":{"UID":{in_or_nin:member_uids[y]}}},
            {"$group":{"_id":"$UID", "Num of Member":{"$sum":1}}}
        ])
        answer[y] = len(list(resultMembers))
    logger.info('member_count %s', answer)
    return answer

def expense_totals(db, member_uids, including=True):
    in_or_nin = '$in' if including else '$nin'
    answer = {}
    for y in member_uids.keys():
        totalPaid = db.claims.aggregate([
            {"$match":{"Year":y}},
            {"$match":{"UID":{in_or_nin:member_uids[y]}}},
            {"$group":{"_id":str(y), "TotalPaid":{"$sum":"$Paid"}}},
        ])
        answer[y] = list(totalPaid)
    logger.info('expense_totals %s', answer)
    return answer

def member_count_having(db, member_uids, condition, including=True):
    in_or_nin = '$in' if including else '$nin'
    answer = {}
    for y in member_uids.keys():
        conds = [
            {"$match":{"Year":y}},
            {"$match":{"UID":{in_or_nin:member_uids[y]}}},
            {"$group":{"_id":"$UID", "TotalPaid":{"$sum":"$Paid"}}},
        ] + [condition]
        logger.info('conditions = %s', conds[0:1]+conds[2:4])
        totalPaid = db.claims.aggregate(conds)
        answer[y] = len(list(totalPaid))
    logger.info('member_count_having %s = %s', condition, answer)
    return answer

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

        Year=["12","14","15"]
        partMember = participating_member_uids(db, Year)
        answer_dict = member_count(db, partMember)
        logger.info('%.2f members_participating_raw, %s', time.time() - t0, answer_dict)
        return answer_dict

    def expenses_participating(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]

        #expenses for each year
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        partMember = participating_member_uids(db, Year)

        answer_dict = expense_totals(db, partMember)

        members = self.members_participating_raw()
        logger.info('self.members_participating_raw: %s', members)
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('%.2f expenses_participating, %s', time.time() - t0, answer)
        return answer

    def members_non_participating(self):
        answer_dict = self.members_non_participating_raw()
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_non_participating_raw(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]

        Year=["12","14","15"]
        partMember = participating_member_uids(db, Year)
        answer_dict = member_count(db, partMember, including=False)
        logger.info('%.2f members_non_participating_raw %s', time.time() - t0, answer_dict)
        return answer_dict

    def expenses_non_participating(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        collection = db['claims']

        #members for each year
        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        partMember = participating_member_uids(db, Year)

        answer_dict = expense_totals(db, partMember, including=False)
        members = self.members_non_participating_raw()
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('%.2f expenses_non_participating, %s', time.time() - t0, answer)
        return answer

    def members_engaged(self):
        answer_dict = self.members_engaged_raw()
        answer = [{"_id": str(2000+int(k)), "count":answer_dict[k]} for k in answer_dict.keys() if k != '15']
        return answer

    def members_engaged_raw(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]

        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        engagedMember=engaged_member_uids(db, Year)
        answer = member_count(db, engagedMember)
        logger.info('%.2f Engaged Members by year, %s', time.time() - t0, answer)
        return answer

    def expenses_engaged(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]

        Year=["12","13","14", "15"]
        Year=["12","14","15"]
        engagedMember=engaged_member_uids(db, Year)
        members = member_count(db, engagedMember)
        answer_dict = expense_totals(db, engagedMember)
        answer = [{"_id":str(2000+int(k)), "dollars": round(answer_dict[k][0]["TotalPaid"]/12.0/members[k], 2)} for k in answer_dict.keys() if k != '15']
        
        logger.info('%.2f Engaged Expenses by year, %s', time.time() - t0, answer)
        return answer

    def figure_3(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        claims = db['claims']

        Year=["12","13","14", "15"]
        Year=["12","14"]
        partMember = participating_member_uids(db, Year)

        lt500 = member_count_having(db, partMember, {"$match":{"TotalPaid": {"$lt":500}}})
        tween = member_count_having(db, partMember, {"$match":{"TotalPaid": {"$lt":10000,"$gt":500}}})
        gt10k = member_count_having(db, partMember, {"$match":{"TotalPaid": {"$gt":10000}}})
        logger.info('lt500 %s', lt500)
        logger.info('tween %s', tween)
        logger.info('gt10k %s', gt10k)

        ret = []
        for y in Year:
            total = lt500[y] + tween[y] + gt10k[y]
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

    def outputReturn(self,groupHigh,groupMe,groupLow,period):
        highGroup=[]
        meGroup=[]
        lowGroup=[]
        group=['High','Medium','Low']
        ans={}
        answer = []

        for i in range(len(group)):
            for item in period:
                ans['Source']='High'
                ans['SourceYear']="20"+item.split('-')[0]
                ans['TargetYear']="20"+item.split('-')[1]
                if i==0:
                    ans['Target']= 'High'
                    ans['Count']=len(set(groupHigh[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
                elif i==1:
                    ans['Target']= 'Medium'
                    ans['Count']=len(set(groupHigh[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
                else:
                    ans['Target']= 'Low'
                    ans['Count']=len(set(groupHigh[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
                highGroup.append(ans) 
                ans={}

        for i in range(len(group)):
            for item in period:
                ans['Source']='Medium'
                ans['SourceYear']="20"+item.split('-')[0]
                ans['TargetYear']="20"+item.split('-')[1]
                if i==0:
                    ans['Target']= 'High'
                    ans['Count']=len(set(groupMe[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
                elif i==1:
                    ans['Target']= 'Medium'
                    ans['Count']=len(set(groupMe[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
                else:
                    ans['Target']= 'Low'
                    ans['Count']=len(set(groupMe[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
                meGroup.append(ans) 
                ans={}

        for i in range(len(group)):
            for item in period:
                ans['Source']='Low'
                ans['SourceYear']="20"+item.split('-')[0]
                ans['TargetYear']="20"+item.split('-')[1]
                if i==0:
                    ans['Target']= 'High'
                    ans['Count']=len(set(groupLow[item.split('-')[0]]).intersection(groupHigh[item.split('-')[1]]))
                elif i==1:
                    ans['Target']= 'Medium'
                    ans['Count']=len(set(groupLow[item.split('-')[0]]).intersection(groupMe[item.split('-')[1]]))
                else:
                    ans['Target']= 'Low'
                    ans['Count']=len(set(groupLow[item.split('-')[0]]).intersection(groupLow[item.split('-')[1]]))
                lowGroup.append(ans) 
                ans={}

       
        for i in highGroup:
            answer.append(i)
        for i in meGroup:
            answer.append(i)
        for i in lowGroup:
            answer.append(i)
        #logger.info('outputReturn 5, %s,\n\n%s,\n\n%s', answer['High'], answer['Medium'], answer['Low'])
        return answer

    def risk_participating_changes(self):
        t0 = time.time()
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        logger.info('risk_participating_changes 1')
     
        level=["RiskPrevention","RiskReduction","ChronicCare"]
        Year=['12','13','14','15']
        period=['12-13','13-14','14-15']
        groupHigh = {}
        groupMe = {}
        groupLow = {}
        interResult = {}
       
        for l in level:
            result=db.biometrics.aggregate([
                {"$match": {"Mstat": l}}, 
                { "$group": {"_id": {"Year":"$Year","UID":"$UID","Risk":"$Mstat"}}}
            ])
    
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
        logger.info('risk_participating_changes 2')
        answer = self.outputReturn(groupHigh,groupMe,groupLow,period)
        logger.info('risk_participating_changes 3, %s', answer)
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
    
        engagedMember={}


        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
             } ).distinct("UID")
        for l in level:
            result=db.biometrics.aggregate([
                {"$match": {"Mstat": l}}, 
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},

                { "$group": {"_id": {"Year":"$Year","UID":"$UID","Risk":"$Mstat"}}}
            ])
    
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
        return self.outputReturn(groupHigh,groupMe,groupLow,period)

    
    def answerFunction(self,Year,normal,outofNormal,critical):
        ans={}
        answer=[]
        logger.error('answerFunction %s %s %s %s', Year,normal,outofNormal,critical)
        for y in Year:
            total=float(normal[y]+outofNormal[y]+critical[y])
            try:
                nor=int(round(normal[y]/total*100,0)) 
                oon=int(round(outofNormal[y]/total*100,0))
                cri=int(round(critical[y]/total*100,0))
            except ZeroDivisionError:
                logger.error('answerFunction year %s, total %s', y, total)
                nor = 0
                oon = 0
                cri = 0

            
            ans['Year'] = '20'+y
            ans['normal']=nor
            ans['critical']=cri
            ans['outofNormal']=oon
            answer.append(ans)
            ans={}
        return answer

    def BMIparticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        #Range >=35:
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"BMI":{"$gt":35}}}
            ])
            listres = list(result)
            critical[y]=int(len(listres))
            logger.debug('BMIparticipant %s %s %s', y, int(len(listres)), critical[y])

       #"Range [25,34.9]:"
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"BMI":{"$gt":25,"$lt":34.9}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        #"Range [18.5,24.9]:"
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"BMI":{"$gt":18.5,"$lt":24.9}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)

        logger.debug('BMIResult %s', answer)
        return answer


    def BMIengaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
        #Range >=35:
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"BMI":{"$gt":35}}}
            ])
            critical[y]=int(len(list(result)))

       #"Range [25,34.9]:"
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"BMI":{"$gt":25,"$lt":34.9}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        #"Range [18.5,24.9]:"
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"BMI":{"$gt":18.5,"$lt":24.9}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def systolicParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        #Range >=160:
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Sys":{"$gt":160}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Sys":{"$gt":120,"$lt":159}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Sys":{"$lt":119}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def systolicEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Sys":{"$gt":160}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Sys":{"$gt":120,"$lt":159}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Sys":{"$lt":119}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def diastolicParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        #Range >=160:
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Dia":{"$gt":100}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Dia":{"$gt":80,"$lt":99}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Dia":{"$lt":79}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def diastolicEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Dia":{"$gt":100}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Dia":{"$gt":80,"$lt":99}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Dia":{"$lt":79}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def FBSParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"FasBS":{"$gt":126}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"FasBS":{"$gt":100,"$lt":125}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"FasBS":{"$gt":70,"$lt":99}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def FBSEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"FasBS":{"$gt":126}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"FasBS":{"$gt":100,"$lt":125}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"FasBS":{"$gt":70,"$lt":99}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def TrigParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Trig":{"$gt":500}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Trig":{"$gt":150,"$lt":499}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Trig":{"$lt":149}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def TrigEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Trig":{"$gt":500}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Trig":{"$gt":150,"$lt":499}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Trig":{"$lt":149}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def A1CParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"A1C":{"$gt":6.5}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"A1C":{"$gt":5.7,"$lt":6.4}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"A1C":{"$lt":5.6}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        logger.debug('A1CResult %s', answer)
        return answer

    def A1CEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"A1C":{"$gt":6.5}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"A1C":{"$gt":5.7,"$lt":6.4}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"A1C":{"$lt":5.6}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def LDLParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"LDL":{"$gt":190}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"LDL":{"$gt":160,"$lt":189}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"LDL":{"$lt":159}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def LDLEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"LDL":{"$gt":190}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"LDL":{"$gt":160,"$lt":189}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"LDL":{"$lt":159}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def TcholesParticipant(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Tcholes":{"$gt":240}}}
            ])
            critical[y]=int(len(list(result)))

       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Tcholes":{"$gt":200,"$lt":239}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"Tcholes":{"$lt":199}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def TcholesEngaged(self):
        client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
        db = client[DATABASES['mongo']['NAME']]
        engagedMember={}
        EngagedStatus={'Y':['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance','GraduatetoRP','MedRxActive','GraduateRP','Monthly','movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD'],
               'N':['NotRequired','OptOut','Terminated','Missed','Dismissed','AppealFollowUp']}
        Year=["12","13","14", "15"]
        critical={}
        normal={}
        outofNormal={}
        for y in Year:
            engagedMember[y]=db.biometrics.find(
                {"$and":[
                    {"Year":int(y)},
                    {"Msubs": {"$in":EngagedStatus['Y']}}
                ]
                 } ).distinct("UID")
       
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Tcholes":{"$gt":240}}}
            ])
            critical[y]=int(len(list(result)))

      
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Tcholes":{"$gt":200,"$lt":239}}}
            ])
            outofNormal[y]=int(len(list(result)))
   
        for y in Year:
            result = db.biometrics.aggregate([
                {"$match":{"Year":int(y)}},
                {"$match":{"UID":{"$in":engagedMember["%s"%(y)]}}},
                {"$match":{"Tcholes":{"$lt":199}}}
            ])
            normal[y]=int(len(list(result)))
        answer=self.answerFunction(Year,normal,outofNormal,critical)
        return answer

    def improved_biometrics(self):
        logger.info('improved_biometrics')

        bmiP = self.BMIparticipant()
        bmiE = self.BMIengaged()
        a1cP = self.A1CParticipant()
        a1cE = self.A1CEngaged()
        #logger.info('improved_biometrics %s %s %s %s', bmiP, bmiE, a1cP, a1cE)
        answer = [{'BMI for Participants' : bmiP},
                  {'BMI for Engaged'      : bmiE},
                  {'A1C for Participants' : a1cP},
                  {'A1C for Engaged'      : a1cE},
                 ]
        return answer

def RPCHandler(request):
    logger.info('home.healthmetrics.RPCHandler')
    mObj = RPCMethods()
    return rpc.RPCHandler(request, mObj)
