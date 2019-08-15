import time

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dappx.models import UserMonitor, UserProfileInfo
from dappx.models import GpsCheckin, VideoUpload


def user_profile_dict(user_profile):
    return {
        'name': user_profile.name,
        'email': user_profile.user.email,
        'days_sober': user_profile.days_sober,
        'created_at': time.mktime(user_profile.created_at.timetuple())
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patients(request):
    # find users who have set this user as a monitor
    patients = UserMonitor.objects.filter(
        notify_email=request.user.email).all()

    patients_info = [
        user_profile_dict(
            UserProfileInfo.objects.filter(user=patient.user).first())
        for patient in patients
    ]

    return Response({
        'patients': patients_info
    }, 201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patient_events(request):
    # find users who have set this user as a monitor

    patient = request.GET.get("email")
    user = User.objects.filter(username=patient).first()

    filter_type = request.GET.get("filter_type")

    allowed = UserMonitor.objects.filter(
        notify_email=request.user.email, user=user).first()

    if not allowed:
        return Response({
            'status': "%s not viewable by %s" % (patient, request.user.email)
        })

    if allowed:
        video_events = VideoUpload.objects.filter(user=user).all()
        gps_events = GpsCheckin.objects.filter(user=user).all()
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
                    'created_at': time.mktime(t.timetuple())})

        if filter_type == 'video' or not filter_type:
            for event in video_events:
                t = event.created_at
                events.append({
                    'type': 'video',
                    'url': event.video_api_link(),
                    'created_at': time.mktime(t.timetuple())})

    return Response({
        'events': sorted(events,
                         key=lambda i: i['created_at'], reverse=True)
    })
