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
from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload
from dappx.views import _create_user
from dappx.views import convert_video, notify_gps_checkin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserProfileInfo.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer


class GpsCheckinViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = GpsCheckin.objects.all().order_by('-id')
    serializer_class = GpsCheckinSerializer

    def perform_create(self, serializer):
        notify_gps_checkin(
            self.request.data['lat'],
            self.request.data['lng'],
            self.request.data['msg'],
            self.request.user
        )
        serializer.save(user=self.request.user)


class VideoUploadViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = VideoUpload.objects.all().order_by('-id')
    serializer_class = VideoUploadSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def video_upload(request):
    video = request.data.get('video')
    video = convert_video(video, request.user)
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
    Token.objects.filter(user=user).delete()
    token = Token.objects.get_or_create(user=user)

    data.pop('password')
    data['message'] = "User created"
    data['token'] = token[0].key

    return Response(data)
