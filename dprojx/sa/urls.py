from django.urls import path

from . import views

urlpatterns = [
    path('api/start', views.start, name="start"),
    path('api/stop', views.stop, name="stop"),
]
