from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('profile/<str:pk>',profile,name='employeeProfile'),
    path('',login,name='employeeLogin'),
    path('issue/<str:pk>>',issues,name='issue'),
 
]
