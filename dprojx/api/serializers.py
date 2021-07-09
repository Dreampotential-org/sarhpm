from django.contrib.auth.models import User
from rest_framework import serializers

from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload, OrganizationMember, UserMonitor


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password','first_name']


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


class OrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = '__all__'
        read_only_fields = ['user']


class UserMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMonitor
        fields = '__all__'

    def get_detailed_data(self, instance):
        return {
            'User': UserSerializer(instance.user).data


        }

    def to_representation(self, instance):
        data = super(UserMonitorSerializer, self).to_representation(instance)
        data.update(self.get_detailed_data(instance))
        gps = GpsCheckin.objects.filter(user_id=instance.user_id)
        video = VideoUpload.objects.filter(user_id=instance.user_id)
        if gps is not None:
            Dict = {}
            for item in gps:

                if item.user_id == instance.user_id:
                    logitude = item.lng
                    latitude = item.lat
                    msg = item.msg
                    Dict["gps"] = {
                        "type": "gps",
                        "long": logitude,
                        "latitude": latitude,
                        "message": msg}
            data.update(Dict)
        if video is not None:
            Dict = {}
            for item in video:

                if item.user_id == instance.user_id:
                    videoUrl = item.videoUrl
                    created_at = item.created_at
                    id = item.id
                    Dict['video'] = {"type": "video",
                                     "created_date": created_at,
                                     "video_url": videoUrl}

            data.update(Dict)
        return data
