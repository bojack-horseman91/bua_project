from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('',CustomerList.as_view()),
    path('<int:pk>/',CustomerSpecific.as_view()),
    path('createCustomer/',CustomerCreate.as_view()),
    path('deleteCustomer/<int:pk>/',CustomerDeleteSpecific.as_view()),

]
