from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.db import connection
import json

from .serializers import *

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
class buaCreate(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        datas=request.data
        str=""
        list=['First Name', 'Last Name', 'ID', 'Phone Number ', 'Email Address', 'Latitude', 'Longitude','Verified']
        print(datas,request)
        info=[]
        data=datas
        for item in list:
            info.append(data[item])
        with connection.cursor() as cursor:
            
            query='INSERT INTO "Service_Provider" VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
      
            print(query)
            cursor.execute(query,info)
            return Response("Success!!!",status=status.HTTP_201_CREATED)

        