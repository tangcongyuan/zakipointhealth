# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 13:59:59 2015

@author: snehasishbarman
"""

from dw_connection import dw_connect as dw
import pymongo as pmo
import requests as req
import pprint as pp
import csv
import datetime
import json
import bson

class Mongod(object):
    
    def __init__(self):
        pass
    
    def putDataToMongod(self, tablename, usr, password):
        pgt = dw.getPGT(username = usr, password = password)
        query = {"pgtIou":pgt, "table": tablename, "clientId": 2000, "pageSize": 1, "clientName": "sdemo"}
        qr = req.get(dw.DAS_URL + "/memberSearch", params = query)
        if qr is None or "result_sets" not in qr or len(qr.get("result_sets")) == 0:
            return None
        qr = qr.json()
        print qr["result_sets"]
        client = pmo.MongoClient()
        db = client["sbdb"]
        db["ms"].insert_one(qr["result_sets"])
        print "No. of records/documents in ms collection: %d" % df["ms"].count()
        
    def getDataFromMongo(self, database, table):
        client = pmo.MongoClient()
        db = client[database]
        result = db[table].find_one()
        pp.pprint(result)
        print "\n" + json.dumps(result, cls = MJSONEncoder)
        
    def putOneDataToMongo(self, database, table):
        client = pmo.MongoClient()
        db = client[database]
        fl = open("/Users/snehasishbarman/Documents/Official_Work/zakipointhealth/demo/claims.txt", "r+")
        csv_object = csv.DictReader(fl, delimiter = "|")
        try:
            for row in csv_object:
                pp.pprint(row)
                row["DW_UPDATE_DATE"] = datetime.datetime.strptime(row["DW_UPDATE_DATE"], "%Y-%m-%d")
                db[table].insert_one(row)
                break
        except Exception as e:
            print e
        finally:
            fl.close()
            
class MJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, bson.ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
        
                
if __name__ == "__main__":
    md = Mongod()
    md.putDataToMongod("ms", "snehasish.barman@zakipoint.com", "Snehasish@123")
    md.getDataFromMongo("sbzph", "medclaims2")
    md.putOneDataToMongo("sbzph", "medclaims2")