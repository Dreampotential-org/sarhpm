from django.urls import path

from . import views

# XXX rename to routes

urlpatterns = [
    path('api/start', views.start, name="start"),
    path('api/stop', views.stop, name="stop"),
    path('api/session_point', views.session_point,
         name="session_point"),
    path('api/get_distances', views.get_distances,
         name="get_distances"),
    path('api/stats', views.get_session_stats, name="get_session_stats"),
]
