from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('',buaList.as_view()),
    path('<int:pk>/',buaSpecific.as_view()),
    path('createBua/',buaCreate.as_view()),
    path('deleteBua/<int:pk>/',buaDeleteSpecific.as_view()),

]
