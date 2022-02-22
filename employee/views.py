from django.shortcuts import render,redirect
from django.db import connection
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")

def strip(s):
    ans=''
    for a in s:
        if a!=' ':
            ans+=a
    return ans

def profile(request,pk):
    context={}
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from "Employee" WHERE ID=%s',[pk])
        row=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        # row['location']=geolocator.geocode(row['Latitude']+","+row['Longitude'])
        context['emp']=row
    print(context)
    return render(request,'Employee page/Employee home.html',context)

def issues(request,pk):
    context={}
    with connection.cursor() as cursor:
        if request.method=='POST':
            print(request.POST)
            if request.POST['type']=='tec':
                cursor.execute('UPDATE "EmployeeTechRelation" set "solved"=1 where "IssueID"=%s',[request.POST['ID']])
            else:
                cursor.execute('UPDATE "EmployeeServRelation" set "solved"=1 where "serviceID"=%s',[request.POST['ID']])
        cursor.execute('SELECT * from "Employee" WHERE ID=%s',[pk])
        row=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
        context['emp']=row
        cursor.execute('SELECT ID,"Description"  from "EmployeeTechRelation" e JOIN "techIssue" t ON t.ID=e."IssueID" WHERE "EmployeeID"=%s AND "solved"=0',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT * FROM "CustomerTechIssue" T JOIN "Customer" C ON C.ID=T."customerID" WHERE T.ID=%s',[r['ID']])
            a=cursor.fetchall()
            if len(a)>0:
                r['type']='Customer'
                a=dict(zip([strip(col[0]) for col in cursor.description],a[0]))
                r['location']=geolocator.geocode(a['Latitude']+","+a['Longitude'])
                r['a']=a
            cursor.execute('SELECT * FROM "buaTechIssue" T JOIN "Service_Provider" C ON C.ID=T."buaID" WHERE T.ID=%s',[r['ID']])
            a=cursor.fetchall()
            if len(a)>0:
                r['type']='BUA'
                a=dict(zip([col[0] for col in cursor.description],a[0]))
                r['location']=geolocator.geocode(a['Latitude']+","+a['Longitude'])
                r['a']=a

        context['tech']=reqs
        cursor.execute('SELECT t."Description",ID from "EmployeeServRelation" e JOIN "ServiceIssue" t ON t.ID=e."serviceID" WHERE "employeeID"=%s AND "solved"=0',[pk])
        reqs=[
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()]
        for r in reqs:
            cursor.execute('SELECT * FROM "customerServiceIssue" T JOIN "Customer" C ON C.ID=T."CustomerID" WHERE T.ID=%s',[r['ID']])
            a=cursor.fetchall()
            if len(a)>0:
                r['type']='Customer'
                a=dict(zip([strip(col[0]) for col in cursor.description],a[0]))
                r['location']=geolocator.geocode(a['Latitude']+","+a['Longitude'])
                r['a']=a
            cursor.execute('SELECT * FROM "BuaServiceIssue" T JOIN "Service_Provider" C ON C.ID=T."BuaID" WHERE T.ID=%s',[r['ID']])
            a=cursor.fetchall()
            if len(a)>0:
                r['type']='BUA'
                a=dict(zip([col[0] for col in cursor.description],a[0]))
                r['location']=geolocator.geocode(a['Latitude']+","+a['Longitude'])
                r['a']=a
        context['serv']=reqs
    print(context)
    return render(request,'Employee page/Issues.html',context)
def auth(phoneNumber,password):
    id=None
    with connection.cursor() as cursor:
        cursor.execute('SELECT ID from "Employee" WHERE "PhoneNumber"=%s and "password"=%s',[phoneNumber,password])
        row=cursor.fetchone()
        if row==None:
            return row
        print(row)
        id=dict(zip(['ID'],row))
    return id['ID']

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
            return redirect('employeeProfile',str(id))
    return render(request,'Employee page/login.html',context)