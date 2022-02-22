from django.shortcuts import render,redirect
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db import connection
import json
from .utils import *
import folium
import geocoder
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

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
            cursor.execute('INSERT INTO "customerServiceIssue" VALUES(%s,%s)',[pk,ID])
            cursor.execute('SELECT  getEmployeeForServ from dual')
            employee=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "EmployeeServRelation"("employeeID","serviceID") VALUES(%s,%s)',[employee,ID])
            return redirect('customerHome',str(pk))
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']={x.replace(' ', ''):v for x, v in r.items()}
        print(context['customer'])
        print(context)
        
    return render(request,'customer/Service issues.html',context)

def tech(request,pk):
    context={}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        if request.method=='POST':
            print(request.POST)
            cursor.execute('SELECT techIssueSeq."NEXTVAL" FROM DUAL;')
            ID=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "techIssue" VALUES(%s,%s)',[ID,request.POST['des']])
            cursor.execute('INSERT INTO "CustomerTechIssue" VALUES(%s,%s)',[pk,ID])
            cursor.execute('SELECT  getEmployeeForTech from dual')
            employee=[ x for x in cursor.fetchone() ][0]
            cursor.execute('INSERT INTO "EmployeeTechRelation"("EmployeeID","IssueID") VALUES(%s,%s)',[employee,ID])
            return redirect('customerHome',str(pk))
       
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']={x.replace(' ', ''):v for x, v in r.items()}
        print(context['customer'])
        print(context)
    return render(request,'customer/Technical issues.html',context)

def completed(request,pk):
    context={}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        if request.method=='POST':
            p=request.POST
            cursor.callproc('buaRatingUpdate',[p['rating'],p['trans'],p['bua']])
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']={x.replace(' ', ''):v for x, v in r.items()}
        print(context['customer'])
        cursor.execute('SELECT * FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is not NULL and "Completed" is not NULL  order by  "time" DESC',[r['ID']])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT  "PhoneNumber","FirstName","LastName","ID",RATING_FUNCTION("Rating") AS "Rating" FROM "Service_Provider"  WHERE "ID"=%s',[r['ServiceProvider_ID']])
            r['bua']=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
            cursor.execute('SELECT "buaRating" FROM "Transaction" WHERE ID=%s',[r['ID']])
            r['rating']=[x for x in cursor.fetchone()][0]
            
        
        context['work']=reqs
        
        print(context)
    return render(request,'customer/Completed jobs.html',context)

def update(request,pk):
    context={}
    with connection.cursor() as cursor:
        if request.method=='POST':
            if request.POST['password']==request.POST['confirmPassword']:
                for k,i in request.POST.items():
                    if k!='confirmPassword' and k!='csrfmiddlewaretoken':
                        print(f"UPDATE \"Customer\" SET \"{k}\" = '{i}'  WHERE ID={pk}")
                        cursor.execute(f"UPDATE \"Customer\" SET \"{k}\" = '{i}'  WHERE ID={pk}")
            else:
                context['passwordError']=True
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']={x.replace(' ', ''):v for x, v in r.items()}
        print(r)
        
    return render(request,'customer/Change or update.html',context)

def ongoingWork(request,pk):
    context={}
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']=r
        print(r)
        
        cursor.execute('SELECT * FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is not NULL and "Completed" is  NULL order by  "time" DESC',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT  "PhoneNumber","FirstName","LastName","ID",RATING_FUNCTION("Rating") AS "Rating" FROM "Service_Provider"  WHERE "ID"=%s',[r['ServiceProvider_ID']])
            r['bua']=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
        context['work']=reqs
        print('sadas',reqs)
    return render(request,'customer/Ongoing services.html',context)


def makeRequest(request,pk):
    context={}
    context['services']=getServices()
    print('!!!!!!!!SERVICES ARE !!!',context['services'])
    print(pk)
    with connection.cursor() as cursor:
        if request.method=='POST':
            bua=request.POST['worker']
            transaction=request.POST['transaction']
            cursor.execute('UPDATE "Transaction" SET "ServiceProvider_ID"=%s  WHERE "ID"=%s ',[bua,transaction])
            cursor.execute('UPDATE "Transaction" SET "Hire_Date"=SYSDATE WHERE "ID"=%s ',[transaction])

        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']=r
        print(r)
        
        cursor.execute('SELECT "ID" FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is NULL order by  "time" DESC',[r['ID']])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        
        for req in reqs:
            cursor.execute('SELECT * FROM "BuaAccept" b JOIN "Service_Provider" s on b."BuaID"=s.ID  WHERE "RequestID"= %s',[req['ID']])
            req['buas']=[
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()]
        print('the requesrtd',reqs)
        context['request']=reqs
        print(request.POST)
    return render(request,'customer/Requests.html',context)


def getCurrentLoaction(pk):
     with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Customer" WHERE "ID"=%s',[int(pk)])
            r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            print(r)
            location = geolocator.geocode(r['Latitude']+","+r['Longitude'])
            return location,r['Latitude'],r['Longitude'],r
def map2(request,pk):
    print(request.GET)
    context={'show_setup':False,'id':pk}
    m=folium.Map(zoom_control=10)
    if request.method=='GET':
        location,lat,lon,context['customer']=getCurrentLoaction(pk)
        folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
        context['map']=m._repr_html_()
        context['location']=location
        return render(request,'customer/mapUpdateCustomer.html',context)
    elif request.method=='POST':
        print(request.POST)
        if request.POST.get('cngLocation'):
            location=geocoder.osm(request.POST['address'])
            lat=str(location.lat)
            lon=str(location.lng)
            updateLocation(pk,lat,lon)

            folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
            context['location']=geolocator.geocode(lat+","+lon)
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

            else:
            
            # updateLocation(pk,lat,lon)
                location,lat,lon,context['customer']=getCurrentLoaction(pk)
                folium.Marker([lat,lon],'click me','more info',draggable=True).add_to(m)
                context['location']=location
        context['map']=m._repr_html_()                
        return render(request,'customer/mapUpdateCustomer.html',context)
def profile(request,pk):
    context={}
    print(pk)
    with connection.cursor() as cursor:
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        r['location']=geolocator.geocode(r['Latitude']+","+r['Longitude'])
        context['customer']={x.replace(' ', ''):v for x, v in r.items()}
        print(context['customer'])
    return render(request,'customer/Customer profile.html',context)
def home(request,pk):
    
    context={'task':getServices()}
    print(pk)
    with connection.cursor() as cursor:
        cursor.callproc('WORK_COMPLTED')
        if request.method=='POST':
            print(request.POST)
            cursor.execute('INSERT INTO "Transaction"("Customer_ID","Amount","time") VALUES(%s,%s,SYSDATE) ',[pk,request.POST['amount']])
            workID=getWork_ID(request.POST)
            cursor.execute('SELECT ID FROM "Transaction" WHERE "Customer_ID"=%s ORDER BY "time" DESC fetch first 1 rows only;',[pk])
            transactionID=dict(zip(['ID'],cursor.fetchone()))
            cursor.execute('commit')
            print(transactionID['ID'])
            for work in workID:
                cursor.execute('INSERT into "Required Services" VALUES(%s,%s)',[transactionID['ID'],int(work)])
                cursor.execute('commit')
        
            
        print(pk,'inside profile!!!!!!!!!!!')
        cursor.execute('SELECT * FROM "Customer"  WHERE ID=%s',[int(pk)])
        r=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['customer']=r
        cursor.execute('SELECT * FROM "Service_Provider"')
        Buas=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()
        ]
        # my_loc=(r['Latitude'],r['Longitude'])
        # for bua in Buas:
            
        #     print(geodesic(my_loc,(bua[ 'Latitude'],bua['Longitude'])))
        cursor.execute('SELECT "ID" FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is NULL order by  "time" DESC  fetch FIRST 1 ROWS ONLY',[r['ID']])
        context['previousRequest']=dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        
        cursor.execute('SELECT * FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is not NULL order by  "time" DESC fetch FIRST 1 ROWS ONLY',[r['ID']])
        context['ongoing']=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in context['ongoing']:
            cursor.execute('SELECT  "PhoneNumber","FirstName","LastName","ID",RATING_FUNCTION("Rating") AS "Rating" FROM "Service_Provider"  WHERE "ID"=%s',[r['ServiceProvider_ID']])
            r['bua']=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
        
        print(context['task'])
        cursor.execute('SELECT * FROM "BuaAccept" b JOIN "Service_Provider" s on b."BuaID"=s.ID  WHERE "RequestID"= %s',[context['previousRequest']['ID']])
        context['previousRequest']['buas']=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        print('prev',context['previousRequest'],context['ongoing'])
        
        
        cursor.execute('SELECT * FROM "Transaction" WHERE "Customer_ID"=%s and "ServiceProvider_ID" is not NULL and "Completed" is not NULL  order by  "time" DESC  fetch FIRST 1 ROWS ONLY',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT  "PhoneNumber","FirstName","LastName","ID",RATING_FUNCTION("Rating") AS "Rating" FROM "Service_Provider"  WHERE "ID"=%s',[r['ServiceProvider_ID']])
            r['bua']=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
            cursor.execute('SELECT "buaRating" FROM "Transaction" WHERE ID=%s',[r['ID']])
            r['rating']=[x for x in cursor.fetchone()][0]
        context['completed']=reqs
        for r in context['completed']:
            cursor.execute('SELECT  "PhoneNumber","FirstName","LastName","ID",RATING_FUNCTION("Rating") AS "Rating" FROM "Service_Provider"  WHERE "ID"=%s',[r['ServiceProvider_ID']])
            r['bua']=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            cursor.execute('SELECT "Name" FROM "Required Services" join "Service" on "service ID"="Service_ID" WHERE "transaction ID"=%s ',[r['ID']])
            r['work']=cursor.fetchall()
            cursor.execute('SELECT "buaRating" FROM "Transaction" WHERE ID=%s',[r['ID']])
            r['rating']=[x for x in cursor.fetchone()][0]
        print(context)
    return render(request,'customer/Customer-home2.html',context)

def login(request):
    context={'error_Message':False}
    print(request.POST)
    if request.method=='POST':
        postInfo=request.POST
        print(postInfo['password'])
        id=auth(postInfo['phoneNumber'],postInfo['password'])
        if id==None:
            context['error_Message']=True
        else:
            print(id)
            return redirect('customerProfile',str(id))
    return render(request,'customer/login for employee.html',context)
class CustomerList(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        data=request.data
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Customer";')
            row = dictfetchall(cursor=cursor)
            row=json.dumps(row)
            print(row)
            return Response(row,status=status.HTTP_200_OK)
class CustomerSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'SELECT * FROM "Customer"  WHERE Customer_ID={pk};')
            cursor.execute(f'SELECT * FROM "Customer"  WHERE Customer_ID={pk};')
            row = dictfetchone(cursor=cursor)
            row=json.dumps(row)
            print(row)
            return Response(row,status=status.HTTP_200_OK)
class CustomerDeleteSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'DELETE FROM "Customer"  WHERE Customer_ID={pk};')
            cursor.execute(f'DELETE FROM "Customer"  WHERE Customer_ID={pk};')
            return Response("Success!!!",status=status.HTTP_200_OK)
def createCustomer(request):
    context={'passwordError':False,'uniquePhoneError':False}
    if request.method=='GET':

        return render(request,'customer/Sign-up-User.html',context)
    else:
        postInfo=request.POST
        print(postInfo)
        info=getMainCustomerInfo(postInfo)
        if not passwordMatch(postInfo['password'],postInfo['comfirmPassword']):
            context['passwordError']=True
            print('pass')
        if not checkPhoneUnique(int(postInfo['phoneNumber'])):
            print('phone')
            context['uniquePhoneError']=True
        if not context['uniquePhoneError'] and not context['passwordError']: 
            id=insertCustomer(postInfo,info)
            
            return redirect(f"map/{id}")
        return render(request,'customer/Sign-up-User.html',context)
    
class CustomerCreate(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        datas=request.data
        with connection.cursor() as cursor:
            list=['First Name', 'Last Name', 'Customer_ID', 'Phone Number ', 'Email Address', 'Latitude', 'Longitude']
            print(datas,request)
            info=[]
            data=datas
            for item in list:
                info.append(data[item])
            query='INSERT INTO "Customer" VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
      
            print(query)
            cursor.execute(query,info)
            return Response("Success!!!",status=status.HTTP_201_CREATED)

        