from django.db import models
from django.contrib.auth.models import User


class VideoUpload(models.Model):
    videoUrl = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.videoUrl


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, blank=True)

    def __str__(self):
        return self.user.username
