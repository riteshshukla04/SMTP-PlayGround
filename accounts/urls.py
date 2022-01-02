from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/', views.indexapi),
    path('inbox/', views.inbox),
    path('bulk/', views.excelMails),
    path('api/inbox', views.inboxapi),
    path('schedule/',views.ScheduleMails),
    path('login/',views.Login),
]
