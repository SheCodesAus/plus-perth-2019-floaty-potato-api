from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

class MovieId(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)

    def __str__ (self):
        return self.title

class Classification(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=10, null=False)
    image = models.ImageField(upload_to = 'classifications/', default = 'no-img.png')

    def __str__ (self):
        return self.text

class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to = 'genres/', default = 'no-img.png')

    def __str__ (self):
        return self.name

class Provider(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to = 'providers/', default = 'no-img.png')

    def __str__ (self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=100, null=False)
    summary = models.CharField(max_length=5000, null=True)
    duration = models.DurationField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to = '', default = 'no-img.png')
    classification = models.ForeignKey(Classification, on_delete=models.DO_NOTHING, null=True)
    genre = models.ManyToManyField(Genre, blank=True)
    provider = models.ManyToManyField(Provider, blank=True)

    def __str__ (self):
        return self.title

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(max_length=8, null=True)
    avatar = models.ImageField(upload_to = 'avatar/', default = 'popcorn.jpg', null=True)
    preferred_genres = models.ManyToManyField(Genre, blank=True)
    preferred_providers = models.ManyToManyField(Provider, blank=True)
    watchlist = models.ManyToManyField(Movie, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ when a new user is created, create the user profile """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ when the user is saved, save the profile """
    instance.profile.save()