from django.urls import path

from . import views

urlpatterns = [
    path('api/start', views.start, name="start"),
    path('api/stop', views.stop, name="stop"),
    path('api/session_point', views.session_point,
         name="session_point"),
]
