
# coding: utf-8

# so i need to tell a story to describe the things I did.

# In[2]:

import pandas as pd
import json
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
MemberData = pd.read_csv(
    "/Users/Kevin/Desktop/Job_Opportunity/zaki/Members.csv")


# this is the top 5% cost members, which is sorted by the totalPaidAmount, and we could find from the risk score, the
# high risk score mainly existed in the top 5% cost members.

# In[3]:

top5CostMember = MemberData.sort_index(
    by='totalPaidAmount', ascending=False)[:500]

top5CostMemberRisk = top5CostMember['riskScore'].dropna()
AllMemberRisk = MemberData['riskScore'].dropna()
plt.ylim(200)
plt.subplot(1, 2, 1)
plt.hist(np.array(top5CostMemberRisk), bins=40)
plt.subplot(1, 2, 2)
plt.ylim(0, 200)
plt.hist(np.array(AllMemberRisk), bins=40)
pl.show()


# we could find the difference between the top cost members and the normal
# members

# to predict the risk score. based on the data.

# In[4]:

x = [1, 2]
y = [AllMemberRisk.mean(), top5CostMemberRisk.mean()]
my_xticks = ["AllMember", "Top5Member"]
plt.subplot(1, 2, 1)
plt.xticks(x, my_xticks)
plt.ylabel("Average RiskScore")
plt.bar(x, y)
plt.subplot(1, 2, 2)
plt.ylabel("Median RiskScore")
y = [AllMemberRisk.median(), top5CostMemberRisk.median()]
plt.bar(x, y)
plt.show()


# perform join the claims and member dataset, we could find the conditions of the members,which is the diagnosis code of
# the member.

# In[3]:

Med_claim = pd.read_csv(
    "/Users/Kevin/Desktop/Job_Opportunity/zaki/med_claims_all.csv")


# random number from 1-5 = quality

# In[4]:

#result = concat([df1, s1], axis=1)
import random
from pandas import Series
lista = []
for i in xrange(len(Med_claim)):
    lista.append(random.randint(1, 5))
result = pd.concat(
    [Series(lista), Med_claim[['providerName', 'providerZip', 'paidAmount']]], axis=1)
result = result.rename(columns={0: 'quality'})
result


# Find the provider with the name "hospital"

# In[5]:

result['tag'] = 1
import re
b = re.compile("Hospital")
j = 0
for i in result.providerName:
    if re.search(b, i):
        result.loc[j, "tag"] = 0
    j += 1


# In[12]:

def f(x):
    return Series([x['paidAmount'].sum(), x['quality'].mean()], index=['cost', 'avgQual'])


# In[14]:

with open('/Users/Kevin/Desktop/Job_Opportunity/zaki/bubble.json', 'w') as outfile:
    json.dump(result[result['tag'] == 0][['quality', 'providerName', 'providerZip', 'paidAmount']].groupby(
        ['providerName', 'providerZip']).apply(f).reset_index().T.to_dict().values(), outfile)


# In[83]:

with open('/Users/Kevin/Desktop/Job_Opportunity/zaki/bubble.json', 'w') as outfile:
    json.dump(result[result['tag'] == 0][
              ['quality', 'providerName', 'providerZip', 'paidAmount']].T.to_dict().values(), outfile)


# In[69]:

Med_claim[Med_claim['tag'] == 0][['providerName', 'providerZip', 'paidAmount']].groupby(
    ['providerName'])    .apply(lambda x: x['paidAmount'].mean())


# this is to try to get the pmpm based on the different relationship id

# In[15]:

# Med_claim.groupby("paidDateMonthYear")
gb = Med_claim[['paidAmount', 'memberId', 'paidDateMonthYear']][Med_claim[
    'relationshipId'] == 'E'].groupby(['paidDateMonthYear', 'memberId']).sum()
gb.reset_index()[['paidDateMonthYear', 'paidAmount']].groupby(
    'paidDateMonthYear').mean().to_json("/Users/Kevin/Desktop/Job_Opportunity/zaki/R_E.json")
gb = Med_claim[['paidAmount', 'memberId', 'paidDateMonthYear']][Med_claim[
    'relationshipId'] == 'S'].groupby(['paidDateMonthYear', 'memberId']).sum()
gb.reset_index()[['paidDateMonthYear', 'paidAmount']].groupby(
    'paidDateMonthYear').mean().to_json("/Users/Kevin/Desktop/Job_Opportunity/zaki/R_S.json")
gb = Med_claim[['paidAmount', 'memberId', 'paidDateMonthYear']][Med_claim[
    'relationshipId'] == 'C'].groupby(['paidDateMonthYear', 'memberId']).sum()
gb.reset_index()[['paidDateMonthYear', 'paidAmount']].groupby(
    'paidDateMonthYear').mean().to_json("/Users/Kevin/Desktop/Job_Opportunity/zaki/R_C.json")


# In[9]:

gb = Med_claim[['paidAmount', 'memberId', 'paidDateMonthYear']].groupby(
    ['paidDateMonthYear', 'memberId']).sum()
gb.reset_index()[['paidDateMonthYear', 'paidAmount']].groupby(
    'paidDateMonthYear').mean().to_json("/Users/Kevin/Desktop/Job_Opportunity/zaki/R_ALL.json")


# for each provider,to make sure their quality and cost.

# In[6]:

Member_claim = pd.merge(
    top5CostMember, Med_claim, left_on='memberSSN', right_on='memberSSN', how='inner')


# In[ ]:

# try to put the diagnosis description and diagnosis code together
Med_claim.diagnosisCode3
Med_claim.diagnosisCode3


# In[44]:

Med_claim[['DiagnosisCode1', 'diagnosisCodeDescription1', 'diagnosisCode3',
           'diagnosisCodeDescription2', 'diagnosisCodeDescription3']]


# In[7]:

import re
import math
DiagNetwork = {}
b = re.compile("[d,D]iagnosisCode\d")

for i in Member_claim.keys():
    if re.match(b, i):
        for j in Member_claim[i]:
            try:
                math.isnan(float(j))
            except:
                if j not in DiagNetwork.keys():
                    DiagNetwork[j] = 1
                else:
                    DiagNetwork[j] += 1
print DiagNetwork


# In[43]:

# if we focus on the primary diagnosis code
# feel confused with primaryDiagCode and primaryDiagnosisCode
# Member_claim.primaryDiagCode
Member_claim.primaryDiagnosis
# Member_claim.primaryDiagnosisCode


# In[ ]:

find the totalpaid for each provider id based on the same diagnosis.


# In[ ]:

import re
import math
DiagNetwork = {}
b = re.compile("[d,D]iagnosisCode\d")

for i in Member_claim.keys():
    if re.match(b, i):
        for j in Member_claim[i]:
            try:
                math.isnan(float(j))
            except:
                if j not in DiagNetwork.keys():
                    DiagNetwork[j] = 1
                else:
                    DiagNetwork[j] += 1
print DiagNetwork


# In[12]:

pd.Series(DiagNetwork).order(ascending=False)


# try to find the diag description

# In[25]:

x = range(len(DiagNetwork))
y = DiagNetwork.values()
plt.bar(x, y)
plt.show()


# this is the readmission rate for the top cost members, and the normal members

# In[ ]:

to find the member conditions based on the readmission.


# In[39]:

# primaryDiagnosis
top5CostMember[(top5CostMember.readmitSevenDayReadmit == 1)]


# In[40]:

pl.subplot(1, 2, 1)
pl.hist(np.array(top5CostMember['readmitSevenDayReadmit'].dropna()))
pl.subplot(1, 2, 2)
pl.hist(np.array(MemberData['readmitSevenDayReadmit'].dropna()))
pl.show()
pl.subplot(1, 2, 1)
pl.hist(np.array(top5CostMember['readmitFifteenDayReadmit'].dropna()))
pl.subplot(1, 2, 2)
pl.hist(np.array(MemberData['readmitFifteenDayReadmit'].dropna()))
pl.show()
pl.subplot(1, 2, 1)
pl.hist(np.array(top5CostMember['readmitThirtyDayReadmit'].dropna()))
pl.subplot(1, 2, 2)
pl.hist(np.array(MemberData['readmitThirtyDayReadmit'].dropna()))
pl.show()
pl.subplot(1, 2, 1)
pl.hist(np.array(top5CostMember['readmitInpatientAdmit'].dropna()))
pl.subplot(1, 2, 2)
pl.hist(np.array(MemberData['readmitInpatientAdmit'].dropna()))
pl.show()


# In[ ]:

risk score in time stamp


# compare the normal and the top cost member's claims are in/out network

# In[52]:

SizeDict = {'y': 0, 'n': 0}
for i in np.array(Med_claim.inOutNetworkFlag.dropna()):
    if i == u'N':
        SizeDict['n'] += 1
    else:
        SizeDict['y'] += 1
labels = 'y', 'n'
sizes = SizeDict.values()
colors = ['yellowgreen', 'lightcoral']
explode = (0, 0.1)
plt.title("Normal And Top Comparision")
plt.subplot(1, 2, 1)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')

top5CostMember_claim = pd.merge(
    top5CostMember, Med_claim, left_on='memberSSN', right_on='memberSSN', how='inner')
SizeDict = {'y': 0, 'n': 0}
for i in np.array(top5CostMember_claim.inOutNetworkFlag.dropna()):
    if i == u'N':
        SizeDict['n'] += 1
    else:
        SizeDict['y'] += 1
sizes = SizeDict.values()
plt.subplot(1, 2, 2)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.show()


# In[ ]:

to find the in / out of network's claims' conditions and procedure and service of provider.
to see the provider's distribution


# In[49]:

top5CostMember[["providerId", "totalPaidAmount"]]


# here we could find from the same provider, the average cost for in/out
# network

# In[53]:

Provider_InOutNet_TotalPaid = top5CostMember_claim[
    ["providerId_y", "inOutNetworkFlag", "totalPaidAmount"]].                            groupby(["providerId_y", "inOutNetworkFlag"]).mean()
Provider_InOutNet_TotalPaid


# In[54]:

plt.hist(np.array(Provider_InOutNet_TotalPaid['totalPaidAmount'][
         :, "Y"]), color="b", label="InNetWork", bins=20)
plt.hist(np.array(Provider_InOutNet_TotalPaid['totalPaidAmount'][
         :, "N"]), alpha=0.5, color="r", label="OutOfNetwork", bins=20)
plt.xlabel("totalPaidAmount")
plt.ylabel("Frequency")
plt.legend()
plt.show()


# find the difference between in/out network in average totalpaid

# In[55]:

(Provider_InOutNet_TotalPaid['totalPaidAmount'][
 :, "Y"] - Provider_InOutNet_TotalPaid['totalPaidAmount'][:, "N"]).dropna().order()


# now we look at the gaps in care

# In[5]:


import requests as req
import urllib
from xml.dom import minidom as xmldom
import numpy as np
import pandas as pd

USERNAME = "qijie.pan@zakipoint.com"                     # your username
PASSWORD = "PQJpqj12345!"                     # your password
HOST_URL = "sdemo.makalu.qc.deerwalk.com"
SERVICE_URL = "https://sdemo.makalu.qc.deerwalk.com:8453/j_spring_cas_security_check"
PGT_URL = "https://das-qc.deerwalk.com/secure/receptor"
LOGIN_DOMAIN = "https://login.qc.deerwalk.com"
DAS_URL = "https://das-qc.deerwalk.com"     # domain for deerwalk api endpoints


def getPGT(username=USERNAME, password=PASSWORD):
    """
    This function returns a PGT ticket. PGT Ticket is required for every requests to the API.

    Params:  
        username (str): Username
        password (str): Password

    Returns:  
        str: A PGT Ticket
    """
    sson = req.Session()
    try:
        # Get the Ticket Granting Ticket
        tgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets",
                                                              data=urllib.urlencode({"username": username,
                                                                                     "password": password,
                                                                                     "hostUrl": HOST_URL}))))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in Authentication")
        tgt = tgt_resp.headers["location"].split("/")
        tgt = tgt[len(tgt) - 1]

        # Get the Service Ticket
        st_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets/" + tgt,
                                                             data=urllib.urlencode({"service": SERVICE_URL}))))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in retrieving Service Ticket")
        st = st_resp.text

        # Get the Proxy Granting Ticket
        pgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/serviceValidate",
                                                              data={"service": SERVICE_URL,
                                                                    "ticket": st,
                                                                    "pgtUrl": PGT_URL})))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in retireving PGT")
        element = xmldom.parseString(pgt_resp.text).getElementsByTagNameNS(
            "http://www.yale.edu/tp/cas", "proxyGrantingTicket")
        return str(element[0].childNodes[0].data)
    except Exception as e:
        print e
    finally:
        sson.close()


# Call this function with your username and password to retrieve your PGTIOU
pgt = getPGT(USERNAME, PASSWORD)
print "PGT: %s\n" % pgt


# find the members gaps in care meet the gaps in care
Query = {"pgtIou": pgt,  "clientId": 2000, "clientName": "sdemo", "reportingBasis": "ServiceDate",
         "report": "qualityMetric", "reportingFrom": "2010-10-01", "reportingTo": "2015-03-31"}

data = req.get(DAS_URL + "/esReport", params=Query).json()


# this is to compare with benchmark

# In[2]:

# https://das.deerwalk.com/esReport?clientId=2000&reportingBasis=ServiceDate&reportingTo=2013-10-31&
#     reportingFrom=2012-11-01&comparisonFrom=2011-11-01&comparisonTo=2012-10-31&report=summary&
#     reportingPaidThrough=2013-10-31&comparisonPaidThrough=2012-10-31

# find the members gaps in care meet the gaps in care
Query = {"pgtIou": pgt,  "clientId": 2000, "clientName": "sdemo", "reportingBasis": "ServiceDate",         "report": "summary", "reportingFrom": "2014-04-01", "reportingTo": "2015-03-31",
         "comparisonFrom": "2013-04-01", "comparisonTo": "2014-03-31", "reportingPaidThrough": "2015-03-31",        "comparisonPaidThrough": "2014-03-31", "includes": "benchmark"}

data = req.get(DAS_URL + "/esReport", params=Query).json()
print data


# In[3]:

data['benchmark']


# In[6]:

data['reporting']['Default']['0']


# In[7]:

# this is only one catogory for gaps in care

GIC = {}
for i in data['reporting']['Default'].keys():
    if data['reporting']['Default'][i]['category'] == 'Additional Gaps':
        Query = {"pgtIou": pgt, "table": "ms", "clientId": 2000, "pageSize": data['reporting']['Default'][i]['numerator'], "page": 1, "clientName": "sdemo",             "query": "{'and':[{'qmNumerator.eq':'1'},{'qmMeasure.eq':" + "'" + data[
            'reporting']['Default'][i]['name'] + "'" + "},{'qmToDate.gte':'2010-05-01'},             {'qmFromDate.lte':'2015-05-31'}]}",             "phiCSDate": "06-01-2010", "phiCEDate": "05-31-2015"}
        result = req.get(DAS_URL + "/memberSearch", params=Query).json()
        GIC[data['reporting']['Default'][i]['name']] = result['result_sets']


# In[9]:

GIC['additionalgaps.4']


# In[60]:

# this is only one catogory for gaps in care

GIC2 = {}
for i in data['reporting']['Default'].keys():
    if data['reporting']['Default'][i]['category'] == 'Additional Gaps':
        Query = {"pgtIou": pgt, "table": "ms", "clientId": 2000, "pageSize": data['reporting']['Default'][i]['numerator'], "page": 1, "clientName": "sdemo",             "query": "{'and':[{'qmNumerator.eq':'0'},{'qmMeasure.eq':" + "'" + data[
            'reporting']['Default'][i]['name'] + "'" + "},{'qmToDate.gte':'2010-05-01'},             {'qmFromDate.lte':'2015-05-31'}]}",             "phiCSDate": "06-01-2010", "phiCEDate": "05-31-2015"}
        result = req.get(DAS_URL + "/memberSearch", params=Query).json()
        GIC2[data['reporting']['Default'][i]['name']] = result['result_sets']


# let's compare the risk score between the person meet/not the gaps in care
# it may not be a good example to use the riskscore here.

# In[61]:

plt.hist(np.array(pd.DataFrame(
    GIC['additionalgaps.1']).T.riskScore.dropna()), color="b", label="Meet", bins=20)
plt.hist(np.array(pd.DataFrame(GIC2['additionalgaps.1']).T.riskScore.dropna(
)), alpha=0.3, color="r", label="DontMeet", bins=20)
plt.xlabel("riskScore")
plt.ylabel("Frequency")
plt.title("additionalGaps1")
plt.legend()
plt.show()

plt.hist(np.array(pd.DataFrame(
    GIC['additionalgaps.2']).T.riskScore.dropna()), color="b", label="Meet", bins=20)
plt.hist(np.array(pd.DataFrame(GIC2['additionalgaps.2']).T.riskScore.dropna(
)), alpha=0.3, color="r", label="DontMeet", bins=20)
plt.xlabel("riskScore")
plt.ylabel("Frequency")
plt.title("additionalGaps2")
plt.legend()
plt.show()

plt.hist(np.array(pd.DataFrame(
    GIC['additionalgaps.3']).T.riskScore.dropna()), color="b", label="Meet", bins=20)
plt.hist(np.array(pd.DataFrame(GIC2['additionalgaps.3']).T.riskScore.dropna(
)), alpha=0.3, color="r", label="DontMeet", bins=20)
plt.xlabel("riskScore")
plt.ylabel("Frequency")
plt.title("additionalGaps3")
plt.legend()
plt.show()

plt.hist(np.array(pd.DataFrame(
    GIC['additionalgaps.4']).T.riskScore.dropna()), color="b", label="Meet", bins=20)
#plt.hist(np.array(pd.DataFrame(GIC2['additionalgaps.4']).T.riskScore.dropna()),alpha = 0.5,color="r",label="DontMeet",bins=20)
plt.xlabel("riskScore")
plt.ylabel("Frequency")
plt.title("additionalGaps4")
plt.legend()
plt.show()


# For the gaps in care, we need to find more data from the diagnosis code

# In[62]:

# let's compare the difference in diagnosis for additonalgaps.2
data = pd.DataFrame(GIC2['additionalgaps.2']).T
data['memberSSN'] = data['memberSSN'].dropna().astype(int)
AG2_N_Claim = pd.merge(
    data, Med_claim, left_on='memberSSN', right_on='memberSSN', how='inner')
data = pd.DataFrame(GIC['additionalgaps.2']).T
data['memberSSN'] = data['memberSSN'].dropna().astype(int)
AG2_Y_Claim = pd.merge(
    data, Med_claim, left_on='memberSSN', right_on='memberSSN', how='inner')


# this is to compare their network in/out rate

# In[63]:

SizeDict = {'y': 0, 'n': 0}
for i in np.array(AG2_N_Claim.inOutNetworkFlag.dropna()):
    if i == u'N':
        SizeDict['n'] += 1
    else:
        SizeDict['y'] += 1
plt.subplot(1, 2, 1)
plt.title("Do not meet the complaince")
sizes = SizeDict.values()
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)

SizeDict = {'y': 0, 'n': 0}
for i in np.array(AG2_Y_Claim.inOutNetworkFlag.dropna()):
    if i == u'N':
        SizeDict['n'] += 1
    else:
        SizeDict['y'] += 1
sizes = SizeDict.values()
plt.subplot(1, 2, 2)
plt.title("Meet the complaince")
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.show()


# for this part, we could find for special gaps in care, what kind of diagonosis they will take,based on joining claims
# together. The things we mainly focus on is the difference not the same.

# In[157]:

DiagNetwork = {}
b = re.compile("[d,D]iagnosisCode\d")

for i in AG2_N_Claim.keys():
    if re.match(b, i):
        for j in AG2_N_Claim[i]:
            try:
                math.isnan(float(j))
            except:
                if j not in DiagNetwork.keys():
                    DiagNetwork[j] = 1
                else:
                    DiagNetwork[j] += 1
print pd.Series(DiagNetwork).order(ascending=False)[:10]

for i in AG2_Y_Claim.keys():
    if re.match(b, i):
        for j in AG2_Y_Claim[i]:
            try:
                math.isnan(float(j))
            except:
                if j not in DiagNetwork.keys():
                    DiagNetwork[j] = 1
                else:
                    DiagNetwork[j] += 1
print pd.Series(DiagNetwork).order(ascending=False)[:10]


# to calculate the pmpm

# In[16]:

# from 2010-04-01 to 2015-03-01
Query = {"pgtIou": pgt,  "clientId": 2000, "clientName": "sdemo", "reportingBasis": "ServiceDate",         "report": "pmpmTrending", "eligibilityType":
         "[medical,vision,dental]", "dataView": "PMPM", "reportingFrom": "2010-04-01", "reportingTo": "2015-03-31",        "recordTypes": "[Medical,Pharmacy,Eligibility,Biometrics,HRA]"}

data = req.get(DAS_URL + "/dashboard", params=Query).json()
print data

