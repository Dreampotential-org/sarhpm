"""dprojx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from dappx import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^log-errors/', views.post_slack_errors, name='log-errors'),
    url(r'^record/', views.record_video_screen, name='record'),
    url(r'^video/', views.video, name='video'),
    url(r'^video-monitor/', views.video_monitor, name='video-monitor'),
    url(r'^upload/', views.upload, name='upload'),
    url(r'^gps-checkin/', views.gps_check_in, name='gps-checkin'),
    url(r'^special/', views.special, name='special'),
    url(r'^dappx/', include('dappx.urls')),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    path('create_notify_user/<str:user_hash>/', views.create_notify_user),
    url(r'^monitor/$', views.monitor, name='monitor'),
    url('^', include('django.contrib.auth.urls')),
]# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
