# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:13:34 2015

@author: snehasishbarman
"""

import requests as req
import urllib
from xml.dom import minidom as xmldom
import numpy as np
import pandas as pd
import scipy.stats as stats
import pylab as pl

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

# send a query request
# reponse: JSON
# query = {"pgtIou":pgt, "table": "ms", "clientId": 2000, "pageSize": 10, "page": 1, "clientName": "sdemo"}
# print req.get(DAS_URL + "/memberSearch", params = query).json()

query = {"pgtIou": pgt, "table": "ms", "clientId": 2000,
         "pageSize": 5000, "page": 1, "clientName": "sdemo"}
MemberResult = req.get(DAS_URL + "/memberSearch", params=query).json()
result = pd.DataFrame(MemberResult['result_sets']).T
i = 2
while(i <= 4):
    query = {"pgtIou": pgt, "table": "ms", "clientId": 2000,
             "pageSize": 5000, "page": i, "clientName": "sdemo"}
    MemberResult = req.get(DAS_URL + "/memberSearch", params=query).json()
    temp = pd.DataFrame(MemberResult['result_sets']).T
    result = pd.concat([result, temp], ignore_index=True)
    i += 1

top5CostMember = result.sort_index(by='totalPaidAmount', ascending=False)[:500]

top5CostMemberRisk = top5CostMember['riskScore'].dropna()
AllMemberRisk = result['riskScore'].dropna()
pl.hist(np.array(top5CostMemberRisk), bins=40)
pl.show()
pl.ylim(200)
pl.hist(np.array(AllMemberRisk), bins=40)
pl.show()
