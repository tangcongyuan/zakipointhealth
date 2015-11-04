#
# run it by typing 
#   python manage.py shell < hsirx_fixtures.py > /dev/null
#

from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User, Group
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.core import serializers
import json, logging
logger = logging.getLogger('zakipoint')

from zphalfa.settings import DATABASES
from home.session import *
from home.models import *

from pymongo import MongoClient

# Loading records into the company collection.
# To run it, execute:
#    python manage.py shell < home/hsirx_fixtures.py > /dev/null
#
co_records = [
    {"Name": "City of Cedar Rapids",
     "Logo": "static/dimages/cedar-rapids-logo.png",
     "Members": 1309,
     "Spend": 34034000,
     "PSA": [4.0],
     "Fasting Blood Glucose": [100, 126],
     "A1C": [6.0, 6.5],
     "LDL": [160, 190],
     "BMI": [30, 35],
     "hypertension": {'systolic': [90,100], 'diastolic': [140, 160]},
 }, {"Name": "Tilde Inc.",
     "logo": "static/dimages/tilde.png",
     "Members": "879",
     "Spend": "$12M",
 }
]
client = MongoClient("mongodb://%s:%s" % (DATABASES['mongo']['HOST'], DATABASES['mongo']['PORT']))
db = client[DATABASES['mongo']['NAME']]
companies = db['companies']
for co_record in co_records:
    record = companies.find_one({'Name': co_record['Name']})
    if record:
        companies.find_one_and_replace({'Name': co_record['Name']}, co_record)
    else:
        companies.insert_one(co_record)

print 'cursoring...'
claims = db['claims']
#looped = 0
#print claims.count()
claims_cursor = claims.find()
uids = []


biometrics = db['biometrics']
biometrics_cursor = biometrics.find()

for doc in biometrics_cursor:
    # modify doc ..
    #collection.save(doc)
    try:
        year = int(doc['Year'])
    except:
        year = 1970
    result = db.biometrics.update_one({'_id': doc['_id']}, {"$set": { "Year": year } })

