from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api import views

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'user-profiles', views.UserProfileViewSet)
router.register(r'gps-checkin', views.GpsCheckinViewSet)
# router.register(r'video', views.VideoUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('create-user/', views.create_user, name='create_user'),
    path('video-upload/', views.video_upload, name='video_upload'),
    path('profile/', views.profile, name='profile'),
    path('add-monitor/', views.add_monitor, name='add_monitor'),
    path('remove-monitor/', views.remove_monitor, name='remove_monitor'),
    # path('list-events/', views.list_events, name='list_events'),
]
