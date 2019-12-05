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

def populatemoviedata(request):
    '''
    import providers and populate database
    '''
    providerslist = requests.get('https://apis.justwatch.com/content/providers/locale/en_AU')
    providers = providerslist.json()
    for b in range (len(providers)):
        provider = Provider(
            name=providers[b]['clear_name'],
            id=providers[b]['id']
            )
        provider.save()

    '''
    import classifications and populate database
    '''
    classificationlist = requests.get('https://apis.justwatch.com/content/age_certifications?country=AU&object_type=movie')
    classifications = classificationlist.json()
    for c in range (len(classifications)):
        classification = Classification(
            text=classifications[c]['technical_name'],
            id=classifications[c]['id']
        )
        classification.save()

    '''
    import genres and populate database

    '''
    genrelist = requests.get('https://apis.justwatch.com/content/genres/locale/en_AU')
    genres = genrelist.json()
    for g in range (len(genres)):
        genre = Genre(
            name=genres[g]['translation'],
            id=genres[g]['id']
        )
        genre.save()

    '''
    import movies and create movie objects
    '''
    responseone = requests.get('https://apis.justwatch.com/content/titles/en_AU/popular?body=%7B%22content_types%22:[%22movie%22],%22providers%22:[%22nfx%22],%22page%22:1,%22page_size%22:10%7D')
    popularmovies = responseone.json()
    # for i in range ((len(popularmovies['items']))):
    # id = popularmovies['items'][i]['id']
    for i in range (1):
        id = '44864'
        data = requests.get('https://apis.justwatch.com/content/titles/movie/{}/locale/en_AU'.format(id)).json()
        '''extract providers '''
        providerdata = data.get('offers')
        genredata = data.get('genre_ids')
        service = None
        if providerdata:
            for j in range(len(data['offers'])):
                if data['offers'][j]['monetization_type'] == 'flatrate':
                    service = Provider.objects.get(pk=(data['offers'][j]['provider_id']))
        if genredata:
            for g in range (len(data['genre_ids'])):
                genre = Genre.objects.get(pk=(data['genre_ids'][g]))

        ''' link classification to movie '''
        if data.get('age_certification'):
            classification = Classification.objects.get(text=data.get('age_certification'))
        else:
            classification = None
        ''' create movie object '''
        movie = Movie(
            id=id,
            title= data['title'], 
            summary= data['short_description'], 
            duration=timedelta(minutes=(data.get('runtime'))), 
            release_date=data.get('cinema_release_date'), 
            classification=classification
            )
        movie.save()
        print(movie)
        ''' link provider to movie '''
        if service:
            movie.provider.add(service)
        ''' link genre to  movie '''
        if genredata:
            movie.genre.add(genre)              
        movie.save()
    return render(request, 'populatemovie.html')

