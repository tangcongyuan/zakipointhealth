import json, logging
logger = logging.getLogger('zakipoint')

from zphalfa.settings import DATABASES
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client['dev']
print 'cursoring...'
biometrics = db['biometrics']
biometrics_cursor = biometrics.find()

engaged_values = ['MovetoRR','GraduatetoRRMonthly','NoPCP','MedRxMaintenance',
                   'GraduatetoRP','MedRxActive','GraduateRP','Monthly',
                   'movetorrmonthly','Targeted','RPhDissmissalPart','RPhDismissalMD']

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

iters = 0

for doc in biometrics_cursor:
    # modify doc ..
    #collection.save(doc)
    try:
        year = int(doc['Year'])
    except:
        year = 1970

    try:
        WelS = int(doc['WelS'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'WelS': WelS}} )
    except:
        pass
  
    try:
        BioS = int(doc['BioS'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'BioS': BioS}} )
    except:
        pass
    try:
        Wei = int(doc['Wei'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Wei': Wei}} )
    except:
        pass
    try:
        BMI = float(doc['BMI'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'BMI': BMI}} )
    except:
        pass
    try:
        Wai = int(doc['Wai'])
        result = db.biometrics.update_one({'_id': doc['_id']},{'$set': {'Wai': Wai}} )
    except:
        pass
    try:
        Hip = int(doc['Hip'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Hip': Hip}} )
    except:
        pass
    try:
        Neck = int(doc['Neck'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Neck': Neck}} )
    except:
        pass
    try:
        BFat = int(doc['BFat'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'BFat': BFat}} )
    except:
        pass
    try:
        Sys = int(doc['Sys'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Sys': Sys}} )
    except:
        pass
    try:
        Dia = int(doc['Dia'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Dia': Dia}} )
    except:
        pass
    try:
        Tcholes = int(doc['Tcholes'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Tcholes': Tcholes}} )
    except:
        pass
    try:
        CholesR = float(doc['CholesR'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'CholesR': CholesR}})
    except:
        pass
    try:
        HDL = int(doc['HDL'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'HDL': HDL}} )
    except:
        pass
    try:
        LDL = int(doc['LDL'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'LDL': LDL}} )
    except:
        pass
    try:
        Trig = int(doc['Trig'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Trig': Trig}} )
    except:
        pass
    try:
        FasBS = int(doc['FasBS'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'FasBS': FasBS}} )
    except:
        pass
    try:
        NonfasBS = int(doc['NonfasBS'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'NonfasBS': NonfasBS}} )
    except:
        pass
    try:
        A1C = float(doc['A1C'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'A1C': A1C}} )
    except:
        try:
            HbA1C = float(doc['HbA1C'])
            result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'A1C': HbA1C}} )
        except:
            pass

    try:
        PSA = int(doc['PSA'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'PSA': PSA}} )
    except:
        pass
    try:
        Cotinine = int(doc['Cotinine'])
        result = db.biometrics.update_one({'_id': doc['_id']}, {'$set': {'Cotinine': Cotinine}} )
    except:
        pass


        
#    if doc['HRAStat'] in ['Primary']:
#        participatingYN = 'Y'
#    else: 
#        participatingYN = 'N'

#    if doc['Msubs'] in engaged_values:
#        engagedYN = 'Y'
#    else: engagedYN = 'N'

#    set_values = {"$set": { "Year": year, 'CoGroup': 'City of Cedar Rapids', 'Participating': participatingYN, 'Engaged': engagedYN}, }

#    result = db.biometrics.update_one({'_id': doc['_id']}, set_values )


