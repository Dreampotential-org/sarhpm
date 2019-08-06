from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import requests
import json

from .models import UserMonitor
from .models import UserProfileInfo
from . import email_utils


def get_user_monitors(request):
    user = User.objects.filter(username=request.user.email).first()
    users = UserMonitor.objects.filter(user=user).all()
    return [u.notify_email for u in users]


def get_user_profile(user):
    if not hasattr(user, 'email'):
        return False

    return UserProfileInfo.objects.filter(
        user__username=user.email
    ).first()


def notify_monitors_video(request, event):
    notify_users = get_user_monitors(request)
    if event['event_type'] == "video":
        msg = (
            'Click to play: https://%s' %
            event['video_model'].video_monitor_link()
        )

        profile = get_user_profile(request.user)
        for notify_user in notify_users:
            email_utils.send_raw_email(
                notify_user,  # send report here
                request.user.email,  # replies to goes here
                'Video Checkin from %s' % profile.name,
                msg
            )

        url = 'https://hooks.slack.com/services/'
        url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
        domain_name = Site.objects.last().domain
        data = (
            str("VideoUpload: %s - https://%s%s" % (
                request.user.email,
                domain_name,
                event['uploaded_file_url'])
                ))
        body = {"text": "%s" % data, 'username': 'pam-server'}
        requests.put(url, data=json.dumps(body))


def notify_gps_checkin(lat, lng, msg, request):
    lat_long_url = 'https://www.google.com/maps/place/%s,%s' % (lat, lng)
    msg += "\n\n\n%s" % lat_long_url

    profile = get_user_profile(request.user)
    notify_users = get_user_monitors(request)
    for notify_user in notify_users:
        email_utils.send_raw_email(
            notify_user,  # send report here
            request.user.email,  # replies to goes here
            'GPS Checkin from %s' % profile.name,
            msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    data = "GspCheckin: %s - %s (%s, %s)" % (request.user.email,
                                             msg, lat, lng)
    # data += "\nSite: %s" % request.META['HTTP_HOST']

    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))
