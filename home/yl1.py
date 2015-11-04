
# coding: utf-8

# In[ ]:

from pymongo import MongoClient
import glob
import argparse
from bson.code import Code
from bson.son import SON

parser = argparse.ArgumentParser(description='data uploading')
parser.add_argument('--db', action='store', dest='dbName', help='store the db name')
#parser.add_argument('--col', action='store',dest='dbCollection',help='store the collection name')
result = parser.parse_args()
# connecting to DB
client = MongoClient("mongodb://localhost:27017")
db = client[result.dbName]
biom=db['biometrics']
claims=db['claims']

#eligible members for each year
pipeline1 = [
     {"$group": {"_id": "$Year", "count": {"$sum": 1}}}
 ]
print "eligible member in each year:"
print list(biom.aggregate(pipeline1))

#participating members
pipeline2 = [
    {
        "$group":
            {
                "_id":{"Year":"$Year","Status":"$HRAStat"},
                "count":{"$sum":1}
        }
    }
]
print "participated member in each year:"    
print list(biom.aggregate(pipeline2))

pipeline3 = [ {"$group": {"_id": {'year':"$Year", "UID": "$UID"}, "paid": {"$sum": "$Paid"}}} ]
print "cost by member by year:"    
paids =  list(claims.aggregate(pipeline3))
for paid in paids:
    # {u'_id': {u'UID': u'ZDJmMWQ0ZWZiNTk4', u'year': u'14'}, u'paid': 0}
    if paid['paid']:
        print paid
