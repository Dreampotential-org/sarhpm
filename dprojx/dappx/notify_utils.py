from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import requests
import json

from .models import UserMonitor
from .models import UserProfileInfo
from . import email_utils
from . import constants
from common import config


logger = config.get_logger()


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


def notify_feedback(message, subject, send_to_email, send_from_email):
    email_utils.send_raw_email(
        send_to_email,  # send report here
        send_from_email,  # replies to goes here
        subject,
        message
    )


def notify_monitors_video(request, event):
    notify_users = get_user_monitors(request)
    profile = get_user_profile(request.user)

    if event['video_model'].source:
        msg = (
            "<p>I AM video from %s - "
            "<a href='https://%s'>Click to play</a></p>" %
            (profile.name, event['video_model'].video_source_link())
        )
    else:
        msg = (
            "<p>I AM video from %s - "
            "<a href='https://%s'>Click to play</a></p>" %
            (profile.name, event['video_model'].video_monitor_link())
        )

    logger.info("Sendering notify email to: %s" % notify_users)
    domain_name = Site.objects.last().domain

    for notify_user in notify_users:

        # Check if user is on platform
        if not UserProfileInfo.objects.filter(
            user__username=notify_user,
        ).count():
            send_msg = (
                "<p>You must created an account "
                "<a href='https://%s/signup.html?email=%s'>here</a> "
                "to view first.<p>" % ('m.useiam.com', notify_user)) + msg
        else:
            logger.info("ON PLATFORM: %s" % notify_user)
            send_msg = msg

        footer = (
            "<p><a href='https://medium.com/@useIAM/tips-on-being-an-iam-monitor-953086e01e2d'>Tips on Being an IAM Monitor</a></p><a href='https://m.useiam.com'>Try I AM</a>"
        )

        email_utils.send_raw_email(
            notify_user,  # send report here
            request.user.email,  # replies to goes here
            'Video Checkin from %s' % profile.name,
            send_msg + footer
        )

    logger.info(msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
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
        if not notify_user:
            logger.info("sending email to [%s]" % notify_user)
            continue

        logger.info("sending email to %s" % notify_user)
        email_utils.send_raw_email(
            notify_user,  # send report here
            request.user.email,  # replies to goes here
            'GPS Checkin from %s' % profile.name,
            msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    data = "GspCheckin: %s - %s (%s, %s)" % (request.user.email,
                                             msg, lat, lng)
    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))


def notify_monitor_email(request, notify_email, monitor_user):

    logger.info("invite source: %s" % request.data.get("source"))
    signup_link = (
        "\n\nhttps://%s/signup.html?email=%s"
        % (request.data.get("source"), request.data.get('notify_email')))
    profile = get_user_profile(request.user)

    if monitor_user:
        logger.info("monitor user already exists")
        message = constants.existing_monitor_message
    else:
        logger.info("monitor user does not exist")
        message = constants.existing_monitor_message + signup_link

    email_utils.send_raw_email(
        to_email=request.data.get("notify_email"),
        reply_to=request.user.username,
        subject='useIAM: %s added you as a monitor'
                % profile.name,
        message_text=message)


def notify_monitor(request, notify_email):
    # check to see if notify_email has account

    logger.info("user: %s added notify_email: %s" %
                (request.user.username, notify_email))
    monitor_user = User.objects.filter(
        username=notify_email
    ).first()

    notify_monitor_email(request, notify_email, monitor_user)
