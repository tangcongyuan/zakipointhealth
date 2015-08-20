from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from django_mongodb_engine import *
from djangotoolbox.fields import *

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'cee1'
FIELDS = {'paidAmount': True}
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)


class PMPM:

    def PMPM_E(self):
        COLLECTION_NAME = 'PMPM_E'
        collection = connection[DBS_NAME][COLLECTION_NAME]
        projects = collection.find(projection=FIELDS)[0]
        json_projects = dumps(projects)
        connection.close()
        return json_projects

    def PMPM_C(self):
        COLLECTION_NAME = 'PMPM_C'
        collection = connection[DBS_NAME][COLLECTION_NAME]
        projects = collection.find(projection=FIELDS)[0]
        json_projects = dumps(projects)
        connection.close()
        return json_projects

    def PMPM_S(self):
        COLLECTION_NAME = 'PMPM_S'
        collection = connection[DBS_NAME][COLLECTION_NAME]
        projects = collection.find(projection=FIELDS)[0]
        json_projects = dumps(projects)
        connection.close()
        return json_projects

    def PMPM_ALL(self):
        COLLECTION_NAME = 'PMPM_ALL'
        collection = connection[DBS_NAME][COLLECTION_NAME]
        projects = collection.find(projection=FIELDS)[0]
        json_projects = dumps(projects)
        connection.close()
        return json_projects


class strategy:

    def bubble(self):
        FIELDS = {'cost': True, 'avgQual': True,
                  'providerName': True, 'providerZip': True}
        COLLECTION_NAME = 'bubble'
        collection = connection[DBS_NAME][COLLECTION_NAME]
        projects = collection.find(projection=FIELDS)
        json_projects = dumps(projects)
        connection.close()
        return json_projects
