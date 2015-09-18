#!/usr/bin/env python
""" 
fileProcess.py:
The function of this file is to parse csv file into json format(array of documents)
insert.py:
This file is for inserting the documents into MongoDB
Here, we use "test" as the db
"biometrics" as the collection name
"""

from fileProcess import process_file


def insert_autos(infile, db):
    data = process_file(infile)
    #Inserting into collection "biometrics"
    db.biometrics.insert(data)
    print "import:%i pieces of documents into MongoDB"%(len(data)) 
  
if __name__ == "__main__":
    # Code here is for local use on your own computer.
    from pymongo import MongoClient
    import glob

    # connecting to DB
    client = MongoClient("mongodb://localhost:27017")
    db = client.test

    # reading in all the csv files
    for files in glob.glob("/Users/Lesley/Desktop/bio/*.csv"):
        insert_autos(files, db)
        print db.biometrics.find_one()
