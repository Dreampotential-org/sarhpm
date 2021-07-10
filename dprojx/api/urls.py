from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api import views
from api import views_admin
from api import views_stripe
from api import views_orgs

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'user-profiles', views.UserProfileViewSet)
router.register(r'gps-checkin', views.GpsCheckinViewSet)
router.register(r'video', views.VideoUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('create-user/', views.create_user, name='create_user'),
    path('pay/', views_stripe.pay, name='pay'),
    path('cancel-plan/', views_stripe.cancel_plan, name='cancel_plan'),
    path('cancel-plan-braintree/', views_stripe.cancel_plan_braintree,
          name='cancel_plan_braintree'),
    path('video-upload/', views.video_upload, name='video_upload'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('add-monitor/', views.add_monitor, name='add_monitor'),
    path('remove-monitor/', views.remove_monitor, name='remove_monitor'),
    path('review-video/', views.review_video, name='review_video'),
    path('get-activity/', views.get_activity, name='get_activity'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('get-video-info/', views.get_video_info, name='get_video_info'),
    path('list_organizations/', views.list_organizations, name='list_organizations'),
    path('set-org/', views.set_org, name='set_org'),
    path('list-patients/', views_admin.list_patients, name='list_patients'),
    path('list-patient-events/', views_admin.list_patient_events,
         name='list_patient_events'),
    path('list-patient-events-v2/', views_admin.list_patient_events_v2,
         name='list_patient_events_v2'),
    path(r'send-magic-link/', views.send_magic_link),
    path(r'auth-magic-link/', views.auth_magic_link),

    path('get_organization_member/',
          views_orgs.get_organization_member, name='get_organization_member'),
    path('add_organization_member/',
          views_orgs.add_organization_member, name='add_organization_member'),



    # path('list-events/', views.list_events, name='list_events'),
]
