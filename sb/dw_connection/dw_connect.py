# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:13:34 2015

@author: snehasishbarman
"""

import requests as req
import urllib
from xml.dom import minidom as xmldom

## Development URls
#USERNAME = "xxxxxxxxxx"                     # your username
#PASSWORD = "xxxxxxxxxx"                     # your password
#HOST_URL = "sdemo.makalu.qc.deerwalk.com"
#SERVICE_URL = "https://sdemo.makalu.qc.deerwalk.com:8453/j_spring_cas_security_check"
#PGT_URL = "https://das-qc.deerwalk.com/secure/receptor"
#LOGIN_DOMAIN = "https://login.qc.deerwalk.com"
#DAS_URL = "https://das-qc.deerwalk.com"     # domain for deerwalk api endpoints
#CLIENT_NAME = "sdemo"
#CLIENT_ID = 2000

## Production URLs
USERNAME = "xxxxxxxxxx"                     # your username
PASSWORD = "xxxxxxxxxx"                     # your password
HOST_URL = "zakipoint.makalu.qc.deerwalk.com"
SERVICE_URL = "https://zakipoint.makalu.qc.deerwalk.com/420/j_spring_cas_security_check"
PGT_URL = "https://das-qc.deerwalk.com/secure/receptor"
LOGIN_DOMAIN = "https://login.qc.deerwalk.com"
DAS_URL = "https://das-qc.deerwalk.com"     # domain for deerwalk api endpoints
CLIENT_NAME = "zakipoint"
CLIENT_ID = "3039"


def getPGT(username = USERNAME, password = PASSWORD):
    """
    This function returns a PGT ticket. PGT Ticket is required for every requests to the API.
    
    Params:  
        username (str): Username
        password (str): Password
        
    Returns:  
        str: A PGT Ticket
    """
    req.packages.urllib3.disable_warnings()
    sson = req.Session()
    try:
        # Get the Ticket Granting Ticket
        tgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets", 
                                                          data = urllib.urlencode({"username": username, 
                                                                                   "password": password, 
                                                                                   "hostUrl": HOST_URL}))), verify = False)
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in Authentication")
        tgt = tgt_resp.headers["location"].split("/")
        tgt = tgt[len(tgt)-1]
        #print tgt                                                                         
                
        # Get the Service Ticket
        st_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets/" + tgt, 
                                                         data = urllib.urlencode({"service": SERVICE_URL}))), verify = False)
        if st_resp.status_code >= 400:
            print st_resp.text
            raise Exception("Error occured in retrieving Service Ticket")
        st = st_resp.text
        #print st
        
        # Get the Proxy Granting Ticket
        pgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/serviceValidate", 
                                                          data = {"service": SERVICE_URL, 
                                                                  "ticket": st, 
                                                                  "pgtUrl": PGT_URL})), verify = False)
        if pgt_resp.status_code >= 400:
            print pgt_resp.text
            raise Exception("Error occured in retireving PGT")
        #print pgt_resp.text
        element = xmldom.parseString(pgt_resp.text).getElementsByTagNameNS("http://www.yale.edu/tp/cas", "proxyGrantingTicket")
        return str(element[0].childNodes[0].data)     
    except Exception as e:
        print e
    finally:
        sson.close()
        


# -- Call this function with your username and password to retrieve your PGTIOU -- 
# pgt = getPGT("snehasish.barman@zakipoint.com", "Snehasish@123")
# print "PGT: %s\n" % pgt

# -- send a query request --
# -- reponse: JSON --
# query = {"pgtIou":pgt, "table": "ms", "clientId": CLIENT_ID, "pageSize": 1, "clientName": CLIENT_NAME}
# qr = req.get(DAS_URL + "/memberSearch", params = query, verify = False).json()
# medical_claims = qr["result_sets"]


