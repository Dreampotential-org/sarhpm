import time
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
from dappx.models import MonitorFeedback
from dappx.views import _create_user
from dappx import email_utils
from dappx.views import convert_and_save_video, stream_video
from dappx.notify_utils import notify_gps_checkin, notify_monitor
from dappx.notify_utils import notify_feedback
from dappx import constants
from dappx import utils
from common import config

from django.http import Http404

logger = config.get_logger()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    http_method_names = ['post']


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserProfileInfo.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer

    def list(self, request):
        profile = UserProfileInfo.objects.filter(
            id=request.user.id
        ).first()
        return Response({
            'days_sober': utils.calc_days_sober(profile),
            'sober_date': profile.sober_date,
            'notify_email': profile.notify_email
        })


class GpsCheckinViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = GpsCheckin.objects.all().order_by('-id')
    serializer_class = GpsCheckinSerializer

    def perform_create(self, serializer):
        logger.error("Creating gps event for user %s" % self.request.user)
        gps_checkin = serializer.save(user=self.request.user)
        notify_gps_checkin(
            gps_checkin, self.request
        )
        print("Created...")


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

    data['email'] = data['email'].lower()
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
    notify_email = request.data.get('notify_email').lower()

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

    notify_monitor(request, notify_email)

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


@api_view(['GET'])
def get_video_info(request):
    token = Token.objects.get(key=request.GET.get("token"))

    logger.info("requesting video as user: %s" % token.user.email)
    resp_body = {}

    try:
        int(request.GET.get("id"))
        # if we get here this is gps-checkin
        # test
        video = GpsCheckin.objects.filter(
            id=int(request.GET.get("id"))).first()
        resp_body['type'] = 'gps'
        resp_body['lat'] = video.lat
        resp_body['lng'] = video.lng
        resp_body['msg'] = video.msg
    except ValueError:
        resp_body['type'] = 'video'
        path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
        video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        return Response({
            'status': 'error',
        }, 201)

    profile = UserProfileInfo.objects.filter(
        user__username=video.user.email
    ).first()

    feedbacks = video.monitor_feedback.all()
    video_feedback = [
        {'user': feedback.user.email, 'message': feedback.message,
         'created_at': time.mktime(feedback.created_at.timetuple())}
        for feedback in feedbacks]

    # get monitors of user
    user_monitors = UserMonitor.objects.filter(user=video.user).all()
    user_monitor_emails = [u.notify_email for u in user_monitors]
    logger.info("User %s monitors are %s"
                % (video.user.email, user_monitor_emails))

    resp_body.update({
        'owner_email': video.user.email,
        'feedback': video_feedback,
        'owner_name': profile.name,
        'created_at': time.mktime(video.created_at.timetuple()),
    })
    if token.user.email == video.user.email:
        resp_body['video_owner'] = True
        return Response(resp_body, 201)

    elif token.user.email in user_monitor_emails:
        resp_body['video_owner'] = False
        return Response(resp_body, 201)

    return Response({
        'status': 'error',
    }, 201)


@api_view(['POST'])
def send_feedback(request):
    token = Token.objects.get(key=request.GET.get("token"))
    user = User.objects.filter(username=token.user.email).first()

    try:
        int(request.GET.get("id"))
        # if we get here this is gps-checkin
        # test
        video = GpsCheckin.objects.filter(
            id=int(request.GET.get("id"))).first()
    except ValueError:
        path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
        video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    # XXX todo add fitlering below to check monitor access to video objs

    logger.info("sending feedback as user: %s msg: %s"
                % (token.user.email, request.data.get("message")))

    monitor_feedback = MonitorFeedback.objects.create(
        user=user, message=request.data.get("message"))

    video.monitor_feedback.add(monitor_feedback)

    # email user who created the video the feedback

    profile = UserProfileInfo.objects.filter(
        user__username=token.user.email
    ).first()

    subject = "%s replied to your video submission" % profile.name
    notify_feedback(request.data.get("message"),
                    subject, video.user.email, token.user.email)

    return Response({'status': 'okay'})


@api_view(['GET'])
def review_video(request):
    token = Token.objects.get(key=request.GET.get("token"))
    logger.info("requesting video as user: %s" % token.user.email)
    path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
    video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    if video and token.user.is_superuser:
        return stream_video(request, path)

    # get monitors of user
    user_monitors = UserMonitor.objects.filter(user=video.user).all()
    user_monitor_emails = [u.notify_email for u in user_monitors]
    logger.info("User %s monitors are %s"
                % (video.user.email, user_monitor_emails))

    if token.user.email in user_monitor_emails:
        logger.info("User %s is a monitor for %s"
                    % (token.user.email, video.user.email))
        return stream_video(request, path)

    elif token.user.email == video.user.email:
        logger.info("User is viewing their own video: %s:%s"
                    % (token.user.email, video.user.email))
        return stream_video(request, path)

    raise Http404


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_activity(request):
    user = User.objects.filter(username=request.user.email).first()
    video_events = VideoUpload.objects.filter(user=user).all()
    gps_events = GpsCheckin.objects.filter(user=user).all()
    events = []

    for event in gps_events:
        t = event.created_at
        events.append({
            'type': 'gps',
            'lat': event.lat,
            'lng': event.lng,
            'msg': event.msg,
            'created_at': time.mktime(t.timetuple())})

    for event in video_events:
        t = event.created_at
        events.append({
            'type': 'video',
            'url': event.video_ref_link(),
            'created_at': time.mktime(t.timetuple())})

    return Response({
        'events': sorted(events,
                         key=lambda i: i['created_at'], reverse=True)[0:20]
    })


@api_view(['PUT', 'GET'])
def profile(request):
    logger.info("get profile info %s" % request.user.email)
    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()

    monitors = []

    active_monitor = False

    if request.method == 'PUT':
        if request.data.get('days_sober'):
            profile.days_sober = request.data.get('days_sober')
        if request.data.get('sober_date'):
            profile.sober_date = request.data.get('sober_date')

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
        'days_sober': utils.calc_days_sober(profile),
        'sober_date': profile.sober_date,
        'notify_email': profile.notify_email,
        'active_monitor': active_monitor,
        'monitors': monitors,
        'stripe_subscription_id': profile.stripe_subscription_id,
    }, 201)
