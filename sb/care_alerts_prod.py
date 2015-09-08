# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 16:41:57 2015

@author: snehasishbarman
"""


import sys
sys.path.append("./dw_connection/")

import requests as req
import pprint as pp
from dw_connection import dw_connect as dw
import csv
import pickle
import os
import logging as log

PGT = None
PAGE = 1


def getMembers(size, page):
    query = {"pgtIou":PGT, "table": "ms", "clientId": dw.CLIENT_ID, 
             "pageSize": size, 
             "page": page,
             "clientName": dw.CLIENT_NAME,
             #"query": "{and : [{relationshipId.eq: SP}]}", # {'currentStatus.eq': 'Active'}
             #"fields": "[unblindMemberId, memberId, memberZip, currentStatus, memberCity, memberState, relationshipId, relationshipIdName, rxTotalPaidAmount, medTotalPaidAmount]",
             "phiCSDate": "01-07-2010",
             "phiCEDate": "06-30-2015"
             }
    qr = req.get(dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()
    
def getCareAlerts(memberId, size, page):    
    query = {"pgtIou":PGT, "table": "emp", "clientId": dw.CLIENT_ID, 
             "pageSize": size, 
             "page": page,
             "clientName": dw.CLIENT_NAME,
             #"query": "{and: [{memberId.eq: " + memberId + "}]}",
             "fields": "[CareAlert, memberId]",
             "phiCSDate": "01-07-2010",
             "phiCEDate": "06-30-2015"
             }
    qr = req.get(url = dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()
    

if __name__ == "__main__":
    req.packages.urllib3.disable_warnings()
    if not os.path.exists("./data_folder/mem_care_prod.dat") or not os.path.exists("./data_folder/care_prod.dat"):
        log.info("Fetching records from API")
        PGT = dw.getPGT("snehasish.barman@zakipoint.com", "Snehasish@123")
        print PGT
        qr = getMembers(1,1)
        N_MEMBERS = qr["summary"]["totalCounts"]
        print "Members: %d" % N_MEMBERS
        qr = getCareAlerts(None, 1, 1)
        N_GAPS = qr["summary"]["totalCounts"]
        print "Gaps: %d" % N_GAPS
        qr = getMembers(N_MEMBERS, PAGE)    
        qr_g = getCareAlerts(None, N_GAPS, PAGE)
        qr_gaps = dict()
        for key, val in qr_g["result_sets"].items():
            qr_gaps[val["memberId"]] = val
            del qr_g["result_sets"][key]
        del qr_g
        pickle.dump(qr, open("./data_folder/mem_care_prod.dat", "wb"))
        pickle.dump(qr_gaps, open("./data_folder/care_prod.dat", "wb"))
    qr = pickle.load(open("./data_folder/mem_care_prod.dat", "rb"))
    qr_gaps = pickle.load(open("./data_folder/care_prod.dat", "rb"))
    
    fl_members = open("./data_folder/members_care_prod.csv", "w+")
    fl_care = open("./data_folder/care_alerts_prod.csv", "w+")
    csv_mem = csv.writer(fl_members)
    csv_mem.writerow(["Member_ID", "Zip_Code", "Current_Status", "Relation_Code", "Relationship_Name", "Total_Rx_Cost", "Total_Medical_Cost"])
    csv_care = csv.writer(fl_care)
    csv_care.writerow(["Member_ID", "Alert", "Date_Identified"])
    
    memberIds = set([])
    try:
        for member, val in qr["result_sets"].items():
            if "relationshipId" not in val or val["relationshipId"] != "SP":
                continue
            if "CareAlert" not in qr_gaps[val["memberId"]] or not qr_gaps[val["memberId"]].get("CareAlert"):
                continue
            memberIds.add(val["unblindMemberId"])
            csv_mem.writerow([val.get("unblindMemberId"),
                              val.get("memberZip"),
                              val.get("currentStatus"),
                              #val.get("memberCity"),
                              #val.get("memberState"),
                              val.get("relationshipId"),
                              val.get("relationshipIdName"),
                              val.get("rxTotalPaidAmount"),
                              val.get("medTotalPaidAmount")])
            for doc in qr_gaps[val["memberId"]].get("CareAlert"):
                csv_care.writerow([val["unblindMemberId"], doc.get("alert"), doc.get("startDate")])
            if len(memberIds) % 100 == 0:
                print "Processed: %d" % len(memberIds)
                fl_members.flush()
                fl_care.flush()
    except Exception as err:
        print "Error Occurred"
        print err
    finally:
        print "Total Members Processed: %d" % len(memberIds)
        fl_members.close()
        fl_care.close()