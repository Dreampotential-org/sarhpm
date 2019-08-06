import logging
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.serializers import (
    UserSerializer, UserProfileSerializer, GpsCheckinSerializer,
    VideoUploadSerializer
)
from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload, UserMonitor
from dappx.views import _create_user
from dappx import email_utils
from dappx.views import convert_and_save_video
from dappx.notify_utils import notify_gps_checkin
from dappx import constants

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserProfileInfo.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer

    def list(self, request):
        profile = UserProfileInfo.objects.filter(
            id=request.user.id
        ).first()
        return Response({
            'days_sober': profile.days_sober,
            'notify_email': profile.notify_email
        })


class GpsCheckinViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = GpsCheckin.objects.all().order_by('-id')
    serializer_class = GpsCheckinSerializer

    def perform_create(self, serializer):
        logger.error("Creating gps event for user %s" % self.request.user)
        notify_gps_checkin(
            self.request.data['lat'],
            self.request.data['lng'],
            self.request.data['msg'],
            self.request
        )
        serializer.save(user=self.request.user)


class VideoUploadViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = VideoUpload.objects.all().order_by('-id')
    serializer_class = VideoUploadSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def video_upload(request):
    logger.error("I am here video_upload")
    logger.error(request.FILES)
    logger.error(request.data)
    video = request.data.get('video')
    if not video:
        logger.error("no vidoe file foudn")
        return Response({'message': 'video is required'}, 400)

    video = convert_and_save_video(video, request)
    return Response({'videoUrl': video.videoUrl})


@api_view(['POST'])
def create_user(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email') or not data.get('password'):
        return Response({
            'message': 'Missing parameters. Email and password is required'
        })

    if not data.get('days_sober'):
        data['days_sober'] = '0'

    user = User.objects.filter(username=data['email']).first()

    if user:
        return Response({'message': 'User already exists'})

    _create_user(**data)

    user = User.objects.filter(username=data['email']).first()
    token = Token.objects.get_or_create(user=user)

    data.pop('password')
    data['message'] = "User created"
    data['token'] = token[0].key

    return Response(data)


@api_view(['PUT', 'GET'])
@permission_classes([IsAuthenticated])
def add_monitor(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email')

    # check if notify_email is already set for user
    have = UserMonitor.objects.filter(user=user,
                                      notify_email=notify_email).first()
    if have:
        return Response({
            'msg': '%s is already a monitor user for you',
        }, 201)


    user_monitor = UserMonitor()
    user_monitor.user = user
    user_monitor.notify_email = notify_email
    user_monitor.save()

    return Response({
        'response': 'okay',
    }, 201)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def remove_monitor(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email')
    monitors = UserMonitor.objects.filter(user=user,
                                          notify_email=notify_email).all()
    if monitors:
        UserMonitor.objects.filter(user=user,
                                   notify_email=notify_email).delete()

    return Response({
        'status': 'okay',
    }, 201)


@api_view(['PUT', 'GET'])
def profile(request):

    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()

    monitors = []

    active_monitor = False

    if request.method == 'PUT':
        if request.data.get('days_sober'):
            profile.days_sober = request.data.get('days_sober')

        if request.data.get('notify_email'):

            no_change = False
            if profile.notify_email == request.data.get('notify_email'):
                no_change = True

            profile.notify_email = request.data.get('notify_email')
            monitor_user = User.objects.filter(
                username=profile.notify_email
            ).first()

            if monitor_user and no_change is False:
                email_utils.send_raw_email(
                    to_email=request.data.get("notify_email"),
                    reply_to=request.user.email,
                    subject='useIAM: %s added you as a monitor'
                            % profile.name,
                    message=constants.existing_monitor_message)
            elif not monitor_user and no_change is False:
                url = "https://" + request.META['HTTP_HOST']
                url += "/create_notify_user/" + profile.user_hash
                mail_text = constants.new_monitor_message + url
                email_utils.send_raw_email(
                    to_email=request.data.get("notify_email"),
                    reply_to=request.user.email,
                    subject='useIAM: %s added you as a monitor'
                            % profile.name,
                    message=mail_text)

        profile.save()

    else:
        if profile.notify_email:
            monitor_user = User.objects.filter(
                username=profile.notify_email
            ).first()
            if monitor_user:
                active_monitor = True
        user = User.objects.filter(username=request.user.email).first()
        users = UserMonitor.objects.filter(user=user).all()
        monitors = [u.notify_email for u in users]
    # Check to see to see if monitor_user is on platform

    return Response({
        'days_sober': profile.days_sober,
        'notify_email': profile.notify_email,
        'active_monitor': active_monitor,
        'monitors': monitors,
    }, 201)
