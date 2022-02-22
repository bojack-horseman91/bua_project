from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',createCustomer,name='customerRegister'),
    path('login/',login,name='customerLogin'),
    path('update/<str:pk>',update,name='customerUpdate'),
    path('map/<str:pk>',map2,name='mapCustomerUpdate'),
    path('ongoing/<str:pk>',ongoingWork,name='customerOngoing'),
    path('completed/<str:pk>',completed,name='customerCompleted'),
    path('request/<str:pk>',makeRequest,name='customerRequest'),
    path('techIssue/<str:pk>',tech,name='customerTechIssue'),
    path('servIssue/<str:pk>',serv,name='customerServIssue'),
    path('home/<str:pk>',home,name='customerHome'),
    path('profile/<str:pk>',profile,name="customerProfile"),
    path('api',CustomerList.as_view()),
    path('api/<int:pk>/',CustomerSpecific.as_view()),
    path('api/createCustomer/',CustomerCreate.as_view()),
    path('api/deleteCustomer/<int:pk>/',CustomerDeleteSpecific.as_view()),

]
