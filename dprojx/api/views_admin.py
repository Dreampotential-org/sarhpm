import time
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import response
from dappx.models import UserMonitor, UserProfileInfo
from api.serializers import (UserMonitorSerializer)
from dappx.models import GpsCheckin, VideoUpload
from common import config
import urllib.parse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, pagination

logger = config.get_logger()

def user_profile_dict(user_profile):
    return {
        'name': user_profile.name,
        'email': user_profile.user.email,
        'days_sober': user_profile.days_sober,
        'sober_date': user_profile.sober_date,
        'created_at': time.mktime(user_profile.created_at.timetuple())
    }


def monitor_feedback_dict(feedback):
    return {
        'name': feedback.user.name,
        'email': feedback.user.email,
        'message': feedback.message,
        'created_at': time.mktime(feedback.created_at.timetuple())
    }


def get_user_events(user):
    video_events = VideoUpload.objects.filter(user=user).all()
    gps_events = GpsCheckin.objects.filter(user=user).all()

    events = []
    for event in gps_events:
        t = event.created_at
        events.append({
            'id': event.id,
            'type': 'gps',
            'lat': event.lat,
            'lng': event.lng,
            'msg': event.msg,
            # 'monitor_feedbacks': [monitor_feedback_dict(f)
            #                     for f in event.monitor_feedback],
            'created_at': time.mktime(t.timetuple())})

    for event in video_events:
        t = event.created_at
        events.append({
            'id': event.video_id(),
            'type': 'video',
            'url': event.video_api_link(),
            # 'monitor_feedbacks': [monitor_feedback_dict(f)
            #                     for f in event.monitor_feedback],
            'created_at': time.mktime(t.timetuple())})

    events = sorted(events, key=lambda i: i['created_at'], reverse=True)

    result = user_profile_dict(
        UserProfileInfo.objects.filter(user=user).first()
    )
    result['events'] = events

    return result


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patients(request):
    # find users who have set this user as a monitor
    patients = UserMonitor.objects.filter(
        notify_email=request.user.email).all()

    patients_info = [
        get_user_events(patient.user)
        for patient in patients
    ]

    return Response({
        'patients': patients_info
    }, 201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patient_events(request):
    # find users who have set this user as a monitor

    filter_type = request.GET.get("filter_type")
    patient = urllib.parse.unquote(request.GET.get("email"))
    users = []
    profiles_map = {}

    # get all patients
    if not patient:
        patients = UserMonitor.objects.filter(
            notify_email=request.user.email).all()

        for patient in patients:
            profile = UserProfileInfo.objects.filter(user=patient.user).first()
            profiles_map[patient.user.email] = profile
            users.append(patient.user)

    else:
        user = User.objects.filter(username=patient).first()
        profile = UserProfileInfo.objects.filter(user=user).first()
        profiles_map[user.email] = profile
        allowed = UserMonitor.objects.filter(
            notify_email=request.user.email, user=user).first()

        if not allowed:
            return Response({
                'status': "%s not viewable by %s" % (patient,
                                                     request.user.email)
            })

        users.append(user)

    print("len %s" % len(users))
    video_events = []
    gps_events = []
    for user in users:
        video_events += VideoUpload.objects.filter(user=user).all()
        gps_events += GpsCheckin.objects.filter(user=user).all()

    events = []
    if filter_type == 'gps' or not filter_type:
        for event in gps_events:
            t = event.created_at
            events.append({
                'id': event.id,
                'type': 'gps',
                'lat': event.lat,
                'lng': event.lng,
                'msg': event.msg,
                'name': profiles_map[event.user.email].name,
                'email': event.user.email,
                'created_at': time.mktime(t.timetuple())})

    if filter_type == 'video' or not filter_type:
        for event in video_events:
            t = event.created_at
            events.append({
                'id': event.id,
                'type': 'video',
                'email': event.user.email,
                'name': profiles_map[event.user.email].name,
                'url': event.video_api_link(),
                'created_at': time.mktime(t.timetuple())})

    events = sorted(events, key=lambda i: i['created_at'], reverse=True)

    paginator = PageNumberPagination()
    paginator.page_size = 10

    page = paginator.paginate_queryset(events, request)
    if page is not None:
        return paginator.get_paginated_response(page)

    return Response(events)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patient_events_v2(request):
    # find users who have set this user as a monitor

    filter_type = request.GET.get("filter_type")
    patient = urllib.parse.unquote(request.GET.get("email"))
    users = []
    profiles_map = {}

    # get all patients
    if not patient:
        patients = UserMonitor.objects.filter(
            notify_email=request.user.email).all()

        for patient in patients:
            profile = UserProfileInfo.objects.filter(
                user=patient.user).first()
            profiles_map[patient.user.email] = profile
            users.append(patient.user)

    else:
        user = User.objects.filter(username=patient).first()
        profile = UserProfileInfo.objects.filter(user=user).first()
        profiles_map[user.email] = profile
        allowed = UserMonitor.objects.filter(
            notify_email=request.user.email, user=user).first()

        if not allowed:
            return Response({
                'status': "%s not viewable by %s" % (patient,
                                                     request.user.email)
            })

        users.append(user)

    print("len %s" % len(users))
    video_events = []
    gps_events = []
    for user in users:
        video_events += VideoUpload.objects.filter(user=user).all()
        gps_events += GpsCheckin.objects.filter(user=user).all()

    events = []
    if filter_type == 'gps' or not filter_type:
        for event in gps_events:
            t = event.created_at
            events.append({
                'id': event.id,
                'type': 'gps',
                'lat': event.lat,
                'lng': event.lng,
                'msg': event.msg,
                'name': profiles_map[event.user.email].name,
                'email': event.user.email,
                'created_at': time.mktime(t.timetuple())})

    if filter_type == 'video' or not filter_type:
        for event in video_events:
            t = event.created_at
            events.append({
                'id': event.video_id(),
                'type': 'video',
                'email': event.user.email,
                'name': profiles_map[event.user.email].name,
                'url': event.video_api_link(),
                'created_at': time.mktime(t.timetuple())})

    events = sorted(events, key=lambda i: i['created_at'], reverse=True)

    return Response({
        'events': sorted(events,
                         key=lambda i: i['created_at'], reverse=True)[0:20]
    })


class UserMonitorView(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('name', openapi.IN_QUERY, description="Search by name",
                          type=openapi.TYPE_STRING,
                          required=False, default=None),

    ])
    def get(self, request, *args, **kwargs):
        name = self.request.GET.get("name")
        if name:
            user_monitor = UserMonitor.objects.filter(user__first_name__icontains=name).all()
        else:
            user_monitor = UserMonitor.objects.all()

        #user_monitor = user_monitor.exclude("password")

        paginated_response = self.paginate_queryset(user_monitor)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)


class UserMonitorViewDetails(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    def delete(self, request, *args, **kwargs):
        if kwargs.get('id'):
            user_monitor = UserMonitor.objects.get(id=kwargs.get('id'))
            user_monitor.delete()
            return response.Response("Data Deleted",status=status.HTTP_202_ACCEPTED)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
