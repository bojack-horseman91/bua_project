from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('map/<str:pk>',map2 ,name='map'),
    path('',BuaCreate,name='buaRegister'),
    path('update/<str:pk>',update,name='buaUpdate'),
    path('offers/<str:pk>',availableWorks,name='buaAvailableWork'),
    path('ongoing/<str:pk>',ongoinWorks,name='buaOngoingWork'),
    path('techIssue/<str:pk>',tech,name='buaTechIssue'),
    path('servIssue/<str:pk>',serv,name='buaServIssue'),
    path('completed/<str:pk>',completed,name='buaCompletedWork'),
    path('home/<str:pk>',buaHome,name='buaHome'),
    path('login',login,name='buaLogin'),
    path('profile/<str:pk>',buaProfile,name='buaProfile'),
    path('api/',buaList.as_view()),
    path('<int:pk>/',buaSpecific.as_view()),
    path('api/createBua/',buaCreateApi.as_view()),
    path('api/deleteBua/<int:pk>/',buaDeleteSpecific.as_view()),

]
