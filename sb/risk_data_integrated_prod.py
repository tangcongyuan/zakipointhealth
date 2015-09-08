# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 21:10:59 2015

@author: snehasishbarman
"""

import sys
sys.path.append("./dw_connection/")

from dw_connection import dw_connect as dw
import requests as req
import csv
import pprint as pp
import os
import pickle

PGT = None
PAGES = 1
N_MEMBERS = 100
N_CLINICAL_RECORDS = 1

def getMembers(size, page):
    query = {"pgtIou":PGT, "table": "ms", "clientId": dw.CLIENT_ID, 
             "pageSize": size, 
             "page": page,
             "clientName": dw.CLIENT_NAME,
             #"query": "{and : [{'currentStatus.eq': 'Active'}, {'relationshipId.eq': 'S'}]}",
             #"fields": "[unblindMemberId, memberId, memberZip, memberCity, memberState, relationshipId," +
             #            "relationshipIdName, rxTotalPaidAmount, medTotalPaidAmount]",
             "phiCSDate": "10-01-2009",
             "phiCEDate": "06-30-2015"
             }
    qr = req.get(dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()
    

def getClinicalParameters(memberId, n_records, page):
    query = {"pgtIou":PGT, "table": "mpra", "clientId": dw.CLIENT_ID, 
             "pageSize": n_records, 
             "page": page,
             "clientName": dw.CLIENT_NAME,
             #"query": "{and: [{memberId.eq: " + memberId + "}]}",
             "fields": "[memberId, MaraHistoricalRiskScores, conditionList]",
             "phiCSDate": "10-01-2009",
             "phiCEDate": "06-30-2015"
             }
    qr = req.get(dw.DAS_URL + "/memberSearch", params = query, verify = False)
    return qr.json()


if __name__ == "__main__":
    req.packages.urllib3.disable_warnings()
    if not os.path.exists("./data_folder/mem_risk.dat") or not os.path.exists("./data_folder/risk.dat"):
        print "Fetching records using API"
        PGT = dw.getPGT("snehasish.barman@zakipoint.com", "Snehasish@123")
        print PGT
        print("Pages, Members processed: \n")
        qr = getMembers(1, 1)
        total = N_MEMBERS = qr["summary"]["totalCounts"]
        qr = getClinicalParameters(None, 1, 1)
        N_CLINICAL_RECORDS = qr["summary"]["totalCounts"]
        print "TOTAL MEMBERS: %d, TOTAL CLINICAL RECORDS: %d" % (N_MEMBERS, N_CLINICAL_RECORDS)
        qr = getMembers(N_MEMBERS, 1)
        qr_c = getClinicalParameters(None, N_CLINICAL_RECORDS, 1)
        qr_clp = dict()
        for key, val in qr_c["result_sets"].items():
            qr_clp[val.get("memberId")] = val
            del qr_c["result_sets"][key]
        del qr_c
        pickle.dump(qr, open("./data_folder/mem_risk.dat", "wb"))
        pickle.dump(qr_clp, open("./data_folder/risk.dat", "wb"))
    
    try:
        qr = pickle.load(open("./data_folder/mem_risk.dat", "rb"))
        qr_clp = pickle.load(open("./data_folder/risk.dat", "rb"))
        #pp.pprint(qr)
        #pp.pprint(qr_clp)
        
        fl_risk_scores = open("./data_folder/risk_scores_prod.csv", "w+")
        fl_risk_factors = open("./data_folder/risk_factors_prod.csv", "w+")
        fl_members = open("./data_folder/members_risk_prod.csv", "w+")
        csv_rscores = csv.writer(fl_risk_scores)
        csv_rscores.writerow(["Member_ID", "Date_Processed", 
                              "Inpatient_Score", "Outpatient_Score", "Physician_Score", "ER_Score",
                              "Other_Score", "Medical_Score", "Pharmacy_Score", "Total_Score",
                              "Expected_Paid", "Prospective_Estimate"])
        csv_rfactors = csv.writer(fl_risk_factors)
        csv_rfactors.writerow(["Member_ID", "Condition", "Condition_%"])
        csv_members = csv.writer(fl_members)
        csv_members.writerow(["Member_ID", "Zip_Code", "Relation_Code", "Relationship_Name", "Total_Rx_Cost", "Total_Medical_Cost"])
        memberIds = set([])
        
        #PAGES = total/N_MEMBERS + 1
        #print "PAGES: %d" % PAGES
        for page in xrange(1, (PAGES+1)):
            if "result_sets" in qr and len(qr.get("result_sets")) > 0:
                for member, val in qr["result_sets"].items():
                    if "relationshipId" not in val or val["relationshipId"] != "SP":
                        continue
                    if "MaraHistoricalRiskScores" not in qr_clp[val["memberId"]]:
                        continue
                    memberIds.add(val["unblindMemberId"])
                    csv_members.writerow([val.get("unblindMemberId"),
                                          val.get("memberZip"),
                                          #val.get("memberCity"),
                                          #val.get("memberState"),
                                          val.get("relationshipId"),
                                          val.get("relationshipIdName"),
                                          val.get("rxTotalPaidAmount"),
                                          val.get("medTotalPaidAmount")])
                    for doc in qr_clp[val["memberId"]]["MaraHistoricalRiskScores"]:
                        csv_rscores.writerow([val["unblindMemberId"],
                                              doc.get("processedDate"),
                                              doc.get("prospectiveInpatient"),
                                              doc.get("prospectiveOutpatient"),
                                              doc.get("prospectivePhysician"),
                                              doc.get("erScore"),
                                              doc.get("otherScore"),
                                              doc.get("prospectiveMedical"),
                                              doc.get("prospectivePharmacy"),
                                              doc.get("prospectiveTotal"),
                                              doc.get("concurrentEstimate"),
                                              doc.get("prospectiveEstimate")])
                    if "conditionList" in qr_clp[val["memberId"]]:
                        for cdoc in qr_clp[val["memberId"]]["conditionList"]:
                            if cdoc["conditionPercentage"] > 0:
                                csv_rfactors.writerow([val["unblindMemberId"],
                                                       cdoc["conditionDesc"],
                                                       cdoc["conditionPercentage"]])
                    if len(memberIds) % 100 == 0:
                        print "%d, %d" % (page, len(memberIds))
                        fl_risk_factors.flush()
                        fl_risk_scores.flush()
                        fl_members.flush()
    except Exception as err:
        print "Error occurred"
        print err
    finally:
        print "No. of members processed: %d" % len(memberIds)
        fl_risk_factors.close()
        fl_risk_scores.close()
        fl_members.close()