from django.urls import path
from .views import populatemoviedata, importrelationreferences

app_name = 'movies'
urlpatterns = [
    path('relationshipreferences/', importrelationreferences, name='realationshippreferences'),
    path('populatemovies/', populatemoviedata, name='populatemoviedata')
]