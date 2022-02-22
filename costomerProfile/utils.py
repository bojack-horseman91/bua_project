import socket 
import requests
from django.db import connection
import re
def updateLocation(id,lat,long):
    print('updated')
    with connection.cursor() as cursor:
        
        query='UPDATE "Customer" set "Latitude"= %s  WHERE ID=%s'
        cursor.execute(query,[lat,id])
        query='UPDATE "Customer" set "Longitude"=%s  WHERE ID=%s'
        cursor.execute(query,[long,id])
def auth(phoneNumber,password):
    id=None
    with connection.cursor() as cursor:
        cursor.execute('SELECT ID from "Customer" WHERE "Phone Number"=%s and "password"=%s',[phoneNumber,password])
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
        cursor.execute(f"SELECT * FROM \"Customer\" WHERE \"Phone Number\" = {number} ;")
        return len(cursor.fetchall())==0

def getWork_ID(info):
    reg=re.compile(r'^[0-9]')
    ids=[i for i,x in info.items()]
    ids=list(filter(reg.search, ids))
    return ids

def getCustomerID(phoneNumber):
    id=None
    with connection.cursor() as cursor:
        cursor.execute('SELECT ID from "Customer" WHERE "Phone Number"=%s',[phoneNumber])
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
def getMainCustomerInfo(items):
    list=['firstName','lastName','phoneNumber','Email','password']
    info=[]
    for item in list:
        info.append(items[item])
    return info    
def insertCustomer(postInfo,info):
    with connection.cursor() as cursor:
        lat,lon=defaultLatitude()
        info.append(str(lat))
        info.append(str(lon))
        print('inserting!!!!!!!!',info)
        query='INSERT INTO "Customer" ("First Name","Last Name","Phone Number","Email Address","password","Latitude","Longitude") VALUES(%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,info)
        cursor.execute('SELECT "ID" FROM "Customer" WHERE "Phone Number"=%s',[postInfo['phoneNumber']])
        customer=getCustomerID(postInfo['phoneNumber'])
        print(dictfetchone(cursor))
        return customer
      
