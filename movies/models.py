from django.db import models
from django.contrib.auth import get_user_model


class Classification(models.Model):
    text = models.CharField(max_length=10, null=False)
    image = models.ImageField(upload_to = 'classifications/', default = 'no-img.png')

    def __str__ (self):
        return self.text

class Genre(models.Model):
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to = 'genres/', default = 'no-img.png')

    def __str__ (self):
        return self.name

class Provider(models.Model):
    name = models.CharField(max_length=50, null=False)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to = 'providers/', default = 'no-img.png')

    def __str__ (self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=100, null=False)
    summary = models.CharField(max_length=5000, null=False)
    duration = models.DurationField(blank=True)
    release_date = models.DateField(blank=True)
    image = models.ImageField(upload_to = 'movies/', default = 'no-img.png')
    classification = models.ForeignKey(Classification, on_delete=models.DO_NOTHING)
    genre = models.ManyToManyField(Genre)
    provider = models.ManyToManyField(Provider)

    def __str__ (self):
        return self.title

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(max_length=8, null=True)
    avatar = models.ImageField(upload_to = 'avatar/', default = 'popcorn.jpg', null=True)
    preferred_genres = models.ManyToManyField(Genre)
    preferred_providers = models.ManyToManyField(Provider)
    watchlist = models.ManyToManyField(Movie)

    def __str__(self):
        return self.user.username