from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db import connection
import json
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
        
    
class servicesList(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        data=request.data
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "services";')
            row = dictfetchall(cursor=cursor)
            row=json.dumps(row)
            print(row)
            return Response(row,status=status.HTTP_200_OK)
class servicesSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'SELECT * FROM "services"  WHERE services_ID={pk};')
            cursor.execute(f'SELECT * FROM "services"  WHERE services_ID={pk};')
            row = dictfetchone(cursor=cursor)
            row=json.dumps(row)
            print(row)
            return Response(row,status=status.HTTP_200_OK)
class servicesDeleteSpecific(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        data=request.data
        print("indentifier is ",pk)
        with connection.cursor() as cursor:
            print(f'DELETE FROM "services"  WHERE services_ID={pk};')
            cursor.execute(f'DELETE FROM "services"  WHERE services_ID={pk};')
            return Response("Success!!!",status=status.HTTP_200_OK)
class servicesCreate(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        datas=request.data
        with connection.cursor() as cursor:
            list=['Customer_ID', 'ServiceProvider_ID', 'payment Method','Amount','ID' ]
            info=[]
            data=datas
            for item in list:
                info.append(data[item])
            query='INSERT INTO "services" VALUES(%s,%s,%s,%s,%s)'
      
            print(query)
            cursor.execute(query,info)
            return Response("Success!!!",status=status.HTTP_201_CREATED)

        