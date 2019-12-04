from django.urls import path
from .views import importmovieids, populatemoviedata

app_name = 'movies'
urlpatterns = [
    path('fetchmovieids/', importmovieids, name='fetchmovieids'),
    path('populatemovies/', populatemoviedata, name='populatemoviedata')
]