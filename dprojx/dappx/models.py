from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models

import hashlib


class GpsCheckin(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    msg = models.CharField(max_length=2000, default='')
    lat = models.CharField(max_length=500, default='')
    lng = models.CharField(max_length=500, default='')
    created_at = models.DateTimeField(auto_now_add=True)


class VideoUpload(models.Model):
    videoUrl = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.videoUrl

    def video_source_link(self):
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '%s/review-video.html?id=%s&user=%s' % (self.source, video_id, user_id)


    def video_ref_link(self):
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '/review-video.html?id=%s&user=%s' % (video_id, user_id)

    def video_link(self):
        domain_name = Site.objects.last().domain
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]
        return '%s/video/?id=%s&user=%s' % (domain_name, video_id, user_id)

    def video_monitor_link(self):
        domain_name = Site.objects.last().domain
        url = self.videoUrl.split('/')
        url = self.videoUrl.split('/')
        video_id = url[-1]
        user_id = url[2]

        return '%s/video-monitor/?id=%s&user=%s' % (
            domain_name, video_id, user_id
        )


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, blank=True)
    name = models.CharField(max_length=17, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notify_email = models.EmailField(max_length=512, blank=True, null=True)
    days_sober = models.PositiveIntegerField(default=0)
    user_hash = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.user_hash = hashlib.sha1(
                self.user.email.encode('utf-8')
            ).hexdigest()
        super(UserProfileInfo, self).save(*args, **kwargs)


class UserMonitor(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default="")
    notify_email = models.EmailField(max_length=512, blank=True, null=True)
