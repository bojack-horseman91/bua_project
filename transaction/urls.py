from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('',transactionList.as_view()),
    path('<int:pk>/',transactionSpecific.as_view()),
    path('createtransaction/',transactionCreate.as_view()),
    path('deletetransaction/<int:pk>/',transactionDeleteSpecific.as_view()),

]
