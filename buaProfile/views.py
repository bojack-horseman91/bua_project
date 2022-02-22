from http.client import HTTPResponse
from django.shortcuts import redirect, render
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db import connection
import json
import re
from .serializers import *
import folium
import geocoder
from .utils import *
import json
import cx_Oracle
# Import module
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
 
geolocator = Nominatim(user_agent="geoapiExercises")

def serv(request,pk):
    if 'service' in request.GET:
        context={'service':request.GET['service']}
    else:
        context={'service':-1}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        
        if request.method=='POST':
            cursor.execute('SELECT serviceIssueSeq."NEXTVAL" FROM DUAL;')
            ID=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "ServiceIssue" VALUES(%s,%s,%s)',[ID,request.POST['id'],request.POST['des']])
            cursor.execute('INSERT INTO "BuaServiceIssue" VALUES(%s,%s)',[ID,pk])
            cursor.execute('SELECT  getEmployeeForServ from dual')
            employee=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "EmployeeServRelation"("employeeID","serviceID") VALUES(%s,%s)',[employee,ID])
            return redirect('buaHome',pk)
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['bua']=r
        print(context)
    return render(request,'bua/Service issues.html',context)

def tech(request,pk):
    context={}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        if request.method=='POST':
            cursor.execute('SELECT techIssueSeq."NEXTVAL" FROM DUAL;')
            ID=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "techIssue" VALUES(%s,%s)',[ID,request.POST['des']])
            cursor.execute('INSERT INTO "buaTechIssue" VALUES(%s,%s)',[pk,ID])
            cursor.execute('SELECT  getEmployeeForTech from dual')
            employee=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "EmployeeTechRelation"("EmployeeID","IssueID") VALUES(%s,%s)',[employee,ID])
            return redirect('buaHome',pk)

        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['bua']=r
        print(context)
    return render(request,'bua/Technical issues.html',context)


def completed(request,pk):
    context={}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        if request.method=='POST':
            p=request.POST
            cursor.callproc('customerRatingUpdate',[p['rating'],p['trans'],p['customer']])
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print(r)
        context['bua']=r
        cursor.execute('SELECT * FROM "Transaction" WHERE "ServiceProvider_ID" =%s and "Completed" is not NULL  order by  "time" DESC',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT  * FROM "Customer"  WHERE "ID"=%s',[r['Customer_ID']])
            r['customer']=dict(zip([strip(col[0]) for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
            cursor.execute('SELECT "customerRating" FROM "Transaction" WHERE ID=%s',[r['ID']])
            r['rating']=[x for x in cursor.fetchone()][0]
            
        
        context['work']=reqs
        
        print(context)
    return render(request,'bua/Completed jobs.html',context)


def ongoinWorks(request,pk):
    context={'bua':{}}
    print('inside profile!!!!!!!!!!!')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print(r)
        context['bua']=r
        print(context['bua'])
        cursor.execute('SELECT * FROM "Transaction" WHERE "ServiceProvider_ID"=%s and "Completed" is null order by  "time" DESC',[int(pk)])
        r=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()
        ]
        context['work']=r
        for o in context['work']:
            cursor.execute('SELECT * FROM "Customer" WHERE ID in( SELECT "Customer_ID" from "Transaction" WHERE ID=%s)',[o['ID']])
            o['c']=dict(zip([strip(col[0]) for col in cursor.description], cursor.fetchone()))
            lat,lon=context['bua']['Latitude'],context['bua']['Longitude']
            o['c']['address']=geolocator.geocode(lat+","+lon)
            o['c']['dis']=geodesic((o['c'][ 'Latitude'],o['c']['Longitude']),(lat,lon))
            cursor.execute('SELECT s."Name" from "Required Services" r JOIN "Service" s on s."Service_ID"=r."service ID" WHERE r."transaction ID"=%s',[o['ID']])
            o['work']=[w for w in cursor.fetchall()]
        print(context)
    return render(request,'bua/Ongoing-services.html' ,context)

def availableWorks(request,pk):
    context={'bua':{}}
    print('inside profile!!!!!!!!!!!')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print(r)
        context['bua']=r
        print(context['bua'])
        cursor.execute('SELECT * FROM "Transaction" WHERE "ServiceProvider_ID" is NULL AND ID NOT in (SELECT "RequestID" FROM "BuaAccept" WHERE "BuaID"=%s)',[pk])
        
        r=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()
        ]
        context['work']=r
        my_loc=(context['bua']['Latitude'],context['bua']['Longitude'])
        for work in context['work']:
            
            cursor.execute('SELECT s."Name" from "Required Services" r JOIN "Service" s on s."Service_ID"=r."service ID" WHERE r."transaction ID"=%s',[work['ID']])
            work['work']=[w for w in cursor.fetchall()]
            cursor.execute('SELECT "First Name"||\' \'||"Last Name" as Name  FROM "Customer" WHERE ID= %s ;' ,[4])
            work['customerName']=cursor.fetchone()
            work['distance']=geodesic(my_loc,(work[ 'Latitude'],work['Longitude']))
            work['address']=geolocator.geocode(work['Latitude']+","+work['Longitude'])

        
        if request.method=='POST':
            cursor.execute('INSERT INTO "BuaAccept" VALUES(%s,%s)',[request.POST['id'],pk])
    return render(request,'bua/Available offers.html' ,context)
def strip(s):
    ans=''
    for a in s:
        if a!=' ':
            ans+=a
    return ans
def buaHome(request,pk):
    context={'bua':{}}
    print('inside profile!!!!!!!!!!!')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print(r)
        context['bua']=r
        print(r)
        print(context['bua'])
        q='(SELECT "ID" FROM "Transaction" WHERE  "ServiceProvider_ID" is NULL order by  "time" DESC  fetch FIRST 1 ROWS ONLY) MINUS (SELECT "RequestID" FROM "BuaAccept" where "BuaID" =%s)'
        cursor.execute(q,[pk])
        context['offers']=[dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        cursor.execute('SELECT "ID","Customer_ID" FROM "Transaction" WHERE "ServiceProvider_ID"=%s  order by  "time" DESC fetch FIRST 1 ROWS ONLY',[pk])
        context['ongoing']=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for o in context['offers']:
            cursor.execute('SELECT * FROM "Customer" WHERE ID in( SELECT "Customer_ID" from "Transaction" WHERE ID=%s)',[o['ID']])
            o['c']=dict(zip([strip(col[0]) for col in cursor.description], cursor.fetchone()))
            lat,lon=context['bua']['Latitude'],context['bua']['Longitude']
            o['c']['address']=geolocator.geocode(lat+","+lon)
            o['c']['dis']=geodesic((o['c'][ 'Latitude'],o['c']['Longitude']),(lat,lon))
            cursor.execute('SELECT s."Name" from "Required Services" r JOIN "Service" s on s."Service_ID"=r."service ID" WHERE r."transaction ID"=%s',[o['ID']])
            o['work']=[w for w in cursor.fetchall()]
            cursor.execute('SELECT "Amount" FROM "Transaction" WHERE ID=%s',[o['ID']])
            o['Amount']=[x for x in cursor.fetchone()][0]
        for o in context['ongoing']:
            cursor.execute('SELECT * FROM "Customer" WHERE ID in( SELECT "Customer_ID" from "Transaction" WHERE ID=%s)',[o['ID']])
            o['c']=dict(zip([strip(col[0]) for col in cursor.description], cursor.fetchone()))
            lat,lon=context['bua']['Latitude'],context['bua']['Longitude']
            o['c']['address']=geolocator.geocode(lat+","+lon)
            o['c']['dis']=geodesic((o['c'][ 'Latitude'],o['c']['Longitude']),(lat,lon))
            cursor.execute('SELECT s."Name" from "Required Services" r JOIN "Service" s on s."Service_ID"=r."service ID" WHERE r."transaction ID"=%s',[o['ID']])
            o['work']=[w for w in cursor.fetchall()]
            cursor.execute('SELECT "Amount" FROM "Transaction" WHERE ID=%s',[o['ID']])
            o['Amount']=[x for x in cursor.fetchone()][0]
        print('offer',context['ongoing'])
        cursor.execute('SELECT * FROM "Transaction" WHERE "ServiceProvider_ID" =%s and "Completed" is not NULL  order by  "time" DESC fetch first 1 row only ',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT  * FROM "Customer"  WHERE "ID"=%s',[r['Customer_ID']])
            r['customer']=dict(zip([strip(col[0]) for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
            cursor.execute('SELECT "customerRating" FROM "Transaction" WHERE ID=%s',[r['ID']])
            r['rating']=[x for x in cursor.fetchone()][0]
            
        
        context['completed']=reqs
        
    return render(request,'bua/bua home.html' ,context)

def update(request,pk):
    context={'bua':{},'passwordError':False,'uniquePhoneError':False}
    print('inside profile!!!!!!!!!!!')
    with connection.cursor() as cursor:
        if request.method=='POST':
            # A=cursor.arrayvar(cx_Oracle.NUMBER,getWork_ID(request.POST))
            # print(A,getWork_ID(request.POST))
            # B=cursor.var(cx_Oracle.NUMBER,int(pk))
            print(request.POST)
            cursor.callproc('UPDATE_buaWork',[int(pk)])
            for w in getWork_ID(request.POST):
                print(w)
                cursor.execute('INSERT INTO BUA_WORKS VALUES(%s,%s);',[w,int(pk)])
                cursor.execute('commit;')
            postInfo=request.POST
            if not passwordMatch(postInfo['Password'],postInfo['confirmPass']):
                context['passwordError']=True
                print('pass')
            else:
                reg=re.compile(r'^[0-9]')
                for k,i in request.POST.items():
                    if reg.match(k) or k=='confirmPass' or k=="csrfmiddlewaretoken" or k=='image':
                        continue
                    print(f"UPDATE \"Service_Provider\" SET \"{k}\" = '{i}'  WHERE ID={pk}")
                    cursor.execute(f"UPDATE \"Service_Provider\" SET \"{k}\" = '{i}'  WHERE ID={pk}")
                    

            
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print('bua is ',r)
        context['bua']=r
        print(context['bua'])
        cursor.execute('SELECT s."Name", s."Service_ID" from BUA_WORKS b join "Service" s on s."Service_ID"=b."Service_ID" WHERE b.BUA_ID=%s',[pk])
        rows=cursor.fetchall()
        columns=[col[0] for col in cursor.description]
        context['task']=[dict(zip(columns, row))  for row in rows]
        cursor.execute('SELECT  "Name", "Service_ID" FROM "Service" MINUS SELECT s."Name", s."Service_ID" from BUA_WORKS b join "Service" s on s."Service_ID"=b."Service_ID" WHERE b.BUA_ID=%s',[pk])
        rows=cursor.fetchall()
        columns=[col[0] for col in cursor.description]
        context['rejectTask']=[dict(zip(columns, row))  for row in rows]
        print( context['rejectTask'])
        
            
    # print(request.POST)
        
    return render(request,'bua/Change or update.html',context)

def buaProfile(request,pk):
    context={'bua':{}}
    print('inside profile!!!!!!!!!!!')
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        print(r)
        context['bua']=r
        print(context['bua'])
        cursor.execute('SELECT s."Name" from BUA_WORKS b join "Service" s on s."Service_ID"=b."Service_ID" WHERE b.BUA_ID=%s',[pk])
        work=cursor.fetchall()
        works=[]
        location = geolocator.geocode(context['bua']['Latitude']+","+context['bua']['Longitude'])
        context['bua']['location']=location
        print(location)
        for w in work:
            works.append(w)
        context['work']=works
    return render(request,'bua/Bua Profile.html',context)


def login(request):
    context={'error_Message':False}
    print(request.POST)
    if request.method=='POST':
        postInfo=request.POST
        id=auth(postInfo['phoneNumber'],postInfo['password'])
        if id==None:
            context['error_Message']=True
        else:
            print(id)
            return redirect('buaProfile',str(id))
    return render(request,'bua/login for bua.html',context)

def maptest(request):
    print(request.GET)
    if request.method=='POST':
        print('ok')
    return render(request,'bua/TEST2.html')

def getCurrentLoaction(pk):
     with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
            r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            print(r)
            location = geolocator.geocode(r['Latitude']+","+r['Longitude'])
            return location,r['Latitude'],r['Longitude'],r

def map2(request,pk):
    print(request.GET)
    context={'show_setup':False,'id':pk}
    m=folium.Map(zoom_control=10)
    if request.method=='GET':
            location,lat,lon,context['bua']=getCurrentLoaction(pk)
            folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
            context['map']=m._repr_html_()
            context['location']=location
            return render(request,'bua/mapUpdateBua.html',context)
    elif request.method=='POST':
        print(request.POST)
        if request.POST.get('cngLocation'):
            print(request.POST)
            location=geocoder.osm(request.POST['address'])
            lat=str(location.lat)
            lon=str(location.lng)
            with connection.cursor() as cursor:
                print(lat,lon)
                query='UPDATE "Service_Provider" SET "Latitude"=%s WHERE ID=%s;'
                cursor.execute(query,[lat,int(pk)])
                cursor.execute('commit;')
                query='UPDATE "Service_Provider" SET "Longitude"=%s WHERE ID=%s;'
                cursor.execute(query,[lon,int(pk)])
                cursor.execute('commit;')
                cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
                r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
                print(r['Latitude']+","+r['Latitude'])
                l = geolocator.geocode(r['Latitude']+","+r['Latitude'])
                print('!!!!!!!!!!!!!',l,'----',geolocator.geocode(lat+","+lon))

                cursor.close()
            folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
            context['location']= geolocator.geocode(lat+","+lon)
        if request.POST.get('my_btn'):
            print('ok')
            location=geocoder.osm(request.POST['location'])
            lat=str(location.lat)
            lon=str(location.lng)
            print('new ' ,lon,' ',lat)
            if lat!=None and lon!=None:
                context['show_setup']=True
                folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
                context['location']=geolocator.geocode(lat+","+lon)
                ans=''
                for s in str(request.POST['location']):
                    if s!=' ':
                        ans+=s
                context['address']=ans
                print(context['address'],request.POST['location'])

            else:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT * FROM "Service_Provider" WHERE "ID"=%s',[int(pk)])
                    r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
                    print(r)
                    context['bua']=r
                    location = geolocator.geocode(context['bua']['Latitude']+","+context['bua']['Latitude'])
                    
                    folium.Marker([context['bua']['Latitude'],context['bua']['Latitude']],'click me','more info',draggable=True).add_to(m)
                    context['map']=m._repr_html_()
                    context['location']=location
                    cursor.close()
        context['map']=m._repr_html_()
        return render(request,'bua/mapUpdateBua.html',context)




def BuaCreate(request):
    context={'passwordError':False,'uniquePhoneError':False,'task':getServices()}
    if request.method=='GET':

        return render(request,'bua/Sign-up-Bua.html',context)
    else:
        postInfo=request.POST
        info=getMainBuaInfo(postInfo)
        if not passwordMatch(postInfo['pass'],postInfo['confirmPass']):
            context['passwordError']=True
            print('pass')
        if not checkPhoneUnique(int(postInfo['phoneNumber'])):
            print('phone')
            context['uniquePhoneError']=True
        if not context['uniquePhoneError'] and not context['passwordError']: 
            id=insertBua(postInfo,info)
            
            return redirect(f"map/{id}")
        return render(request,'bua/Sign-up-Bua.html',context)


          





class buaList(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
    
        
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Service_Provider";')
            row = fetchAll2(cursor=cursor)
            print(row)
            buaserial=buasSerializers(data=row,many=True)
            row=json.dumps(row)
            c=[{'content': 'foo bar', 'email': 'leila@example.com',
                },{'content': 'foo sadabar', 'email': 'leila@example.com',
                }]
            if CommentSerializer(data=c,many=True).is_valid():
                print("ok")
            if buaserial.is_valid():
                print(f"buas {buaserial.data}")
            else:
                print("fuck you")
                
            
            return Response(buaserial.data,status=status.HTTP_200_OK)
class buaSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'SELECT * FROM "Service_Provider"  WHERE ID={pk};')
            cursor.execute(f'SELECT * FROM "Service_Provider"  WHERE ID={pk};')
            row = dictfetchone(cursor=cursor)
            row=json.dumps(row)
            print(row)
            return Response(row,status=status.HTTP_200_OK)
class buaDeleteSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'DELETE FROM "Service_Provider"  WHERE ID={pk};')
            cursor.execute(f'DELETE FROM "Service_Provider"  WHERE ID={pk};')
            return Response("Success!!!",status=status.HTTP_200_OK)
class buaCreateApi(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        datas=request.data
        str=""
        list=['Phone Number ','First Name', 'Last Name','password']
        print(datas,request)
        info=[]
        data=datas
        for item in list:
            info.append(data[item])
        with connection.cursor() as cursor:
            print(datas['Phone Number '],type(datas['Phone Number ']))
            cursor.execute(f"SELECT * FROM \"Service_Provider\" WHERE \"PhoneNumber\" = {674573} ;")
            print('sahdaskhdkalshd................',len(cursor.fetchall()))
            query='INSERT INTO "Service_Provider"("PhoneNumber","FirstName","LastName","Password") VALUES(%s,%s,%s,%s)'
      
            print(info)
            cursor.execute(query,info)
            return Response("Success!!!",status=status.HTTP_201_CREATED)

        