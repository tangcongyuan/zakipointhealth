# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 19:07:22 2015

@author: snehasishbarman
"""

import sys
sys.path.append("./dw_connection/")

import requests as req
import pprint as pp
from dw_connection import dw_connect as dw
import csv

PGT = None
PAGE = 1


def getMembers(size, page):
    query = {"pgtIou":PGT, "table": "ms", "clientId": 2000, 
             "pageSize": size, 
             "page": page,
             "clientName": "sdemo",
             "query": "{and : [{'currentStatus.eq': 'Active'}, {'relationshipId.eq': 'S'}]}",
             "fields": "[unblindMemberId, memberId, memberZip, memberCity, memberState, relationshipId," +
                         "relationshipIdName, rxTotalPaidAmount, medTotalPaidAmount]",
             "phiCSDate": "10-01-2009",
             "phiCEDate": "09-30-2014"
             }
    qr = req.get(dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()
    
def getCareAlerts(memberId, size, page):
    query = {"pgtIou":PGT, "table": "emp", "clientId": 2000, 
             "pageSize": size, 
             "page": page,
             "clientName": "sdemo",
             #"query": "{and: [{memberId.eq: " + memberId + "}]}",
             "fields": "[CareAlert, memberId]",
             "phiCSDate": "10-01-2009",
             "phiCEDate": "06-30-2015"
             }
    qr = req.get(url = dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()
    

if __name__ == "__main__":
    req.packages.urllib3.disable_warnings()
    PGT = dw.getPGT("snehasish.barman@zakipoint.com", "Snehasish@123")
    print PGT
    qr = getMembers(1,1)
    N_MEMBERS = qr["summary"]["totalCounts"]
    qr = getCareAlerts(None, 1, 1)
    N_GAPS = qr["summary"]["totalCounts"]
    
    qr = getMembers(N_MEMBERS, PAGE)    
    qr_g = getCareAlerts(None, N_GAPS, PAGE)
    qr_gaps = dict()
    for key, val in qr_g["result_sets"].items():
        qr_gaps[val["memberId"]] = val
        del qr_g["result_sets"][key]
    del qr_g
    
    fl_members = open("/Users/snehasishbarman/Documents/Official_Work/sb/data_folder/members_care.csv", "w+")
    fl_care = open("/Users/snehasishbarman/Documents/Official_Work/sb/data_folder/care_alerts.csv", "w+")
    csv_mem = csv.writer(fl_members)
    csv_mem.writerow(["Member_ID", "Zip_Code", "City", "State", "Relation_Code", "Relationship_Name", "Total_Rx_Cost", "Total_Medical_Cost"])
    csv_care = csv.writer(fl_care)
    csv_care.writerow(["Member_ID", "Alert", "Date_Identified"])
    
    memberIds = set([])
    try:
        for member, val in qr["result_sets"].items():
            if "CareAlert" not in qr_gaps[val["memberId"]] or not qr_gaps[val["memberId"]].get("CareAlert"):
                continue
            memberIds.add(val["unblindMemberId"])
            csv_mem.writerow([val.get("unblindMemberId"),
                              val.get("memberZip"),
                              val.get("memberCity"),
                              val.get("memberState"),
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
            
            
    
    
    
    
    


    
    
