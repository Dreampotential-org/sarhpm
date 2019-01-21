from django.db import models
from django.contrib.auth.models import User


class GpsCheckin(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    msg = models.CharField(max_length=2000, default='')
    lat = models.CharField(max_length=500, default='')
    lng = models.CharField(max_length=500, default='')
    created_at = models.DateTimeField(auto_now_add=True)


class VideoUpload(models.Model):
    videoUrl = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.videoUrl


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, blank=True)
    name = models.CharField(max_length=17, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


def get_user_profile_info_from_user(user_id):
    user = User.objects.get(id=user_id)

