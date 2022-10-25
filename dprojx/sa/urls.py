from django.urls import path

from . import views

urlpatterns = [
    path('api/member_session_start', views.member_session_start,
         name="member_session_start"),
    path('api/member_session_stop', views.member_session_stop,
         name="member_session_stop"),
]
