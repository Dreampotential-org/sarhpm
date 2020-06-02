from django.contrib.auth.models import User
from rest_framework import serializers

from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        exclude = ('password',)


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfileInfo
        fields = ['user']


class GpsCheckinSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = GpsCheckin
        fields = ['msg', 'lat', 'lng', 'user']


class VideoUploadSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = VideoUpload
        fields = ['id', 'user', 'videoUrl']
