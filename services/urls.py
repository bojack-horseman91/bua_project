from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('',servicesList.as_view()),
    path('<int:pk>/',servicesSpecific.as_view()),
    path('createservices/',servicesCreate.as_view()),
    path('deleteservices/<int:pk>/',servicesDeleteSpecific.as_view()),

]
