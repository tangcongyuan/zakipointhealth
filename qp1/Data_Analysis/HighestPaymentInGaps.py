import requests as req
import urllib
from xml.dom import minidom as xmldom

USERNAME = "qijie.pan@zakipoint.com"                     # your username
PASSWORD = "PQJpqj12345!"                     # your password
HOST_URL = "sdemo.makalu.qc.deerwalk.com"
SERVICE_URL = "https://sdemo.makalu.qc.deerwalk.com:8453/j_spring_cas_security_check"
PGT_URL = "https://das-qc.deerwalk.com/secure/receptor"
LOGIN_DOMAIN = "https://login.qc.deerwalk.com"
DAS_URL = "https://das-qc.deerwalk.com"     # domain for deerwalk api endpoints


def getPGT(username=USERNAME, password=PASSWORD):
    """
    This function returns a PGT ticket. PGT Ticket is required for every requests to the API.

    Params:  
        username (str): Username
        password (str): Password

    Returns:  
        str: A PGT Ticket
    """
    sson = req.Session()
    try:
        # Get the Ticket Granting Ticket
        tgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets",
                                                              data=urllib.urlencode({"username": username,
                                                                                     "password": password,
                                                                                     "hostUrl": HOST_URL}))))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in Authentication")
        tgt = tgt_resp.headers["location"].split("/")
        tgt = tgt[len(tgt) - 1]

        # Get the Service Ticket
        st_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/v1/tickets/" + tgt,
                                                             data=urllib.urlencode({"service": SERVICE_URL}))))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in retrieving Service Ticket")
        st = st_resp.text

        # Get the Proxy Granting Ticket
        pgt_resp = sson.send(sson.prepare_request(req.Request("POST", LOGIN_DOMAIN + "/cas/serviceValidate",
                                                              data={"service": SERVICE_URL,
                                                                    "ticket": st,
                                                                    "pgtUrl": PGT_URL})))
        if tgt_resp.status_code >= 400:
            print tgt_resp.text
            raise Exception("Error occured in retireving PGT")
        element = xmldom.parseString(pgt_resp.text).getElementsByTagNameNS(
            "http://www.yale.edu/tp/cas", "proxyGrantingTicket")
        return str(element[0].childNodes[0].data)
    except Exception as e:
        print e
    finally:
        sson.close()


# Call this function with your username and password to retrieve your PGTIOU
pgt = getPGT(USERNAME, PASSWORD)
print "PGT: %s\n" % pgt

# send a query request
# reponse: JSON
# query = {"pgtIou":pgt, "table": "ms", "clientId": 2000, "pageSize": 10, "page": 1, "clientName": "sdemo"}
# print req.get(DAS_URL + "/memberSearch", params = query).json()


# find the members gaps in care meet the gaps in care
GIC = {}
for i in data['reporting']['Default'].keys():
    Query = {"pgtIou": pgt, "table": "ms", "clientId": 2000, "pageSize": data['reporting']['Default'][i]['numerator'], "page": 1, "clientName": "sdemo",
             "query": "{'and':[{'qmNumerator.eq':'1'},{'qmMeasure.eq':" + "'" + data['reporting']['Default'][i]['name'] + "'" + "},{'qmToDate.gte':'2010-05-01'},\
         {'qmFromDate.lte':'2015-05-31'}]}",
             "phiCSDate": "06-01-2010", "phiCEDate": "05-31-2015"}
    result = req.get(DAS_URL + "/memberSearch", params=Query).json()
    print result['result_sets'].keys()
    GIC[data['reporting']['Default'][i]['name']] = result['result_sets']


temp = GIC['wellness.24']['0']
GapsInCareHighestPaidMeet = {}
for i in GIC.keys():
    for j in GIC[i].keys():
        GapsInCareHighestPaidMeet[i] = temp
        if 'totalPaidAmount' in GIC[i][j].keys():
            if temp['totalPaidAmount'] < GIC[i][j]['totalPaidAmount']:
                temp = GIC[i][j]
# to find the highest cost members in each gaps
pd.DataFrame(GapsInCareHighestPaidMeet)
