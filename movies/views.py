from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
import django_filters.rest_framework
from datetime import datetime, timedelta

from .models import Movie, Classification, Provider, Genre, MovieId
from .serializers import MovieSerializer, GenreSerializer, ProviderSerializer, ClassificationSerializer, UserSerializer, ProfileSerializer
from .models import Profile
from .permissions import IsAdminOrSelf, IsAdminUser
from .tokens import account_activation_token
import requests

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]
    renderer_classes = [JSONRenderer]

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    renderer_classes = [JSONRenderer]

class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]
    renderer_classes = [JSONRenderer]

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    renderer_classes = [JSONRenderer]

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created, viewed or edited or deleted.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        permission_classes=[]
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdminOrSelf]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


def activate(request, uidb64, token):    
    """
    what happens when users visit /activate/uid/token to activate account
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def importmovieids(request):
    response = requests.get('https://apis.justwatch.com/content/titles/en_AU/popular?body=%7B%22content_types%22:[%22movie%22],%22page%22:1,%22page_size%22:100%7D')
    data = response.json()
    for i in range((len(data['items']))):
        jwid = data['items'][i]['id']
        title = data['items'][i]['title']
        MovieId(id=jwid, title=title).save()
    return render(request, 'fetchmovieids.html')

def populatemoviedata(request):
    response = requests.get('https://apis.justwatch.com/content/titles/movie/100/locale/en_AU')
    data = response.json()
    classification = Classification.objects.get(pk='1')
    movie = Movie(
        id=data['id'],
        title= data['title'], 
        summary= data['short_description'], 
        duration=timedelta(minutes=(data.get('runtime'))), 
        release_date=data.get('cinema_release_date'), 
        classification=classification)
    movie.save()
    return render(request, 'populatemovie.html')