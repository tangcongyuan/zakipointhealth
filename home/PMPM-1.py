from pymongo import MongoClient
import glob
import argparse
from bson.code import Code
from bson.son import SON

parser = argparse.ArgumentParser(description='data uploading')
parser.add_argument('--db', action='store', dest='dbName', help='store the db name')
parser.add_argument('--col', action='store',dest='dbCollection',help='store the collection name')
result = parser.parse_args()
# connecting to DB
client = MongoClient("mongodb://localhost:27017")
db = client[result.dbName]
collection=db[result.dbCollection]

# calculating the expenses for eligible members
Year=["12","13","14"]
for y in Year:
    resultFees = collection.aggregate([
        {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
        {"$group":{"_id":"%s"%(y), "TotalPaid":{"$sum":"$Paid"}}}
    ])
    print list(resultFees)
    resultMembers = collection.aggregate([
        {"$match":{"IncDate":{"$regex":"%s$"%(y)}}},
        {"$group":{"_id":"%s"%(y), "Num of Member":{"$sum":1}}}
    ])
    print list(resultMembers)