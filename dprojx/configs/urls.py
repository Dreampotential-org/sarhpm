from django.urls import path

from . import views

urlpatterns = [
    path('list_media',
         views.get_mediA, name="list_media"),
]
