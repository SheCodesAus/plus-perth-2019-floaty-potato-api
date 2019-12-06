from django.urls import path
from .views import movieomdbdata

app_name = 'movies'
urlpatterns = [
    path('moviedata/', movieomdbdata, name='movieomdbdata'),
]