from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from movies.views import *
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'classifications', ClassificationViewSet)
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
