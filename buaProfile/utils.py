import socket 
import requests
from django.db import connection
import re
def getMainBuaInfo(items):
    list=['phoneNumber','firstName','lastName','pass']
    info=[]
    for item in list:
        info.append(items[item])
    return info    

def updateLocation(id,lat,long):
    print('updated')
    with connection.cursor() as cursor:
        
        query='UPDATE "Service_Provider" SET "Latitude"=%s WHERE ID=%s;'
        cursor.execute(query,[lat,id])
        cursor.execute('commit;')
        query='UPDATE "Service_Provider" SET "Longitude"=%s WHERE ID=%s;'
        cursor.execute(query,[long,id])
        cursor.execute('commit;')

def auth(phoneNumber,password):
    id=None
    with connection.cursor() as cursor:
        cursor.execute('SELECT "ID" FROM "Service_Provider" WHERE "PhoneNumber"=%s and "Password"=%s',[phoneNumber,password])
        row=cursor.fetchone()
        if row==None:
            return row
        print(row)
        id=dict(zip(['ID'],row))
    return id['ID']

def defaultLatitude():
    hostname = socket.gethostname()   
    IPAddr = socket.gethostbyname(hostname)  
        
    response = requests.get('http://ipinfo.io/json').json()
    print(response)
        
    response = requests.get(f"https://geolocation-db.com/json/{response['ip']}&position=true").json()
    print(response)
    return response['latitude'],response['longitude']


def checkPhoneUnique(number):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM \"Service_Provider\" WHERE \"PhoneNumber\" = {number} ;")
        return len(cursor.fetchall())==0

def getWork_ID(info):
    reg=re.compile(r'^[0-9]')
    ids=[i for i,x in info.items()]
    ids=list(filter(reg.search, ids))
    ids=[int(i) for i in ids]
    return ids

def getBUAid(phoneNumber):
    id=None
    with connection.cursor() as cursor:
        cursor.execute('SELECT "ID" FROM "Service_Provider" WHERE "PhoneNumber"=%s',[phoneNumber])
        row=cursor.fetchone()
        if row==None:
            return row
        id=dict(zip(['ID'],row))
    return id['ID']
def getServices():
    with connection.cursor() as cursor:
            query='SELECT * FROM "Service";'
            cursor.execute(query)
            service=dictfetchall(cursor)
            return service
    return None
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
def dictfetchone(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return  dict(zip(columns, cursor.fetchone()))

def fetchAll2(cursor):
    columns=['firstName', 'lastName', 'ID', 'phoneNumber', 
          'email', 'latitude', 'longitude','verified']
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]       
def passwordMatch(password,conPass):
    return password==conPass

def insertBua(postInfo,info):
    with connection.cursor() as cursor:
        lat,lon=defaultLatitude()
        info.append(lat)
        info.append(lon)
        query='INSERT INTO "Service_Provider"("PhoneNumber","FirstName","LastName","Password","Latitude","Longitude") VALUES(%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,info)
        cursor.execute('SELECT "ID" FROM "Service_Provider" WHERE "PhoneNumber"=%s',[postInfo['phoneNumber']])
        bua=getBUAid(postInfo['phoneNumber'])
        print(dictfetchone(cursor))
        for  work in getWork_ID(postInfo):
            query='INSERT INTO  "BUA_WORKS" VALUES(%s,%s);'
            cursor.execute(query,[int(work),int(bua)])
        return bua
      