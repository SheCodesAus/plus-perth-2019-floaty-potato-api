
import requests
# import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from rest_framework.views import APIView
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta

from .models import Movie, Classification, Provider, Genre
from .serializers import MovieSerializer, GenreSerializer, ProviderSerializer, ClassificationSerializer, UserSerializer, ProfileSerializer
from .models import Profile
from .permissions import IsAdminOrSelf, IsAdminUser
from .tokens import account_activation_token


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['provider','genre', 'classification']
    search_fields = ['title']
    ordering_fields = ['title']
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

    # def get_permissions(self):
    #     permission_classes=[]
    #     if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
    #         permission_classes = [AllowAny]
    #     elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
    #         permission_classes = [IsAdminOrSelf]



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
        return HttpResponseRedirect('/api/users/success')
    else:
        return HttpResponse('Activation link is invalid!')

def activeaccount(request):
    return render (request, 'acc_active_conf.html')

def importrelationreferences(request):
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

    return HttpResponse(status=201)

def populatemoviedata(request):
    '''
    import movies and create movie objects
    '''
    for pagenum in range (21,26):
        responseone = requests.get('https://apis.justwatch.com/content/titles/en_AU/popular?body=%7B%22content_types%22:[%22movie%22],%22monetization_types%22:[%22flatrate%22],%22providers%22:[%22nfx%22,%22ftp%22,%22stn%22,%22prv%22,%22dnp%22,%22ivw%22,%22sbs%22,%22tpl%22],%22page%22:{},%22page_size%22:100%7D'.format(pagenum))
        popularmovies = responseone.json()
        for i in range ((len(popularmovies['items']))):
            id = popularmovies['items'][i]['id']

            data = requests.get('https://apis.justwatch.com/content/titles/movie/{}/locale/en_AU'.format(id)).json()

            ''' fetch movie's classification '''
            if data.get('age_certification'):
                classification = Classification.objects.get(text=data.get('age_certification'))
            else:
                classification = None
            
            ''' create movie object '''
            movie = Movie(
                id=id,
                title= data.get('title'), 
                summary= data.get('short_description'), 
                duration=timedelta(minutes=(data.get('runtime'))), 
                release_date=data.get('cinema_release_date'), 
                classification=classification
                )
            movie.save()

            ''' save movie poster '''
            if data.get('poster'):
                poster = data.get('poster')[:-10]
                imagename = "movies{}.jpg".format(poster)
                r=requests.get('https://images.justwatch.com'+poster+'/s592')
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(r.content)
                img_temp.flush()
                movie.image.save(imagename, File(img_temp), save=True)
            
            ''' link provider to movie '''

            providers = data.get('offers')
            if providers:
                for p in range(len(providers)):
                    if providers[p]['monetization_type'] == 'flatrate':
                        movie.provider.add(Provider.objects.get(pk=(providers[p]['provider_id'])))
            
            ''' link genres to movie '''
            genres = data.get('genre_ids')
            if genres:
                for g in range (len(genres)):
                    movie.genre.add(Genre.objects.get(pk=genres[g]))   

            movie.save()

    return HttpResponse(status=201)

