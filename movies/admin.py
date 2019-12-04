from django.contrib import admin
from .models import Movie, Classification, Provider, Genre, Profile, MovieId

admin.site.register(Movie)
admin.site.register(Classification)
admin.site.register(Provider)
admin.site.register(Genre)
admin.site.register(Profile)
admin.site.register (MovieId)
