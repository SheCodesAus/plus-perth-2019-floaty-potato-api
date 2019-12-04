from django.urls import path
from .views import populatemoviedata

app_name = 'movies'
urlpatterns = [
    path('populatemovies/', populatemoviedata, name='populatemoviedata')
]