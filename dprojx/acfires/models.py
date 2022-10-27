import uuid
import os
from django.db import models

from django.contrib.auth import get_user_model


def uuid_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(filename)


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=uuid_file_path)


class MediA(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=uuid_file_path)
    name = models.CharField(max_length=5128, blank=True, null=True)
    user = models.ForeignKey(to=get_user_model(),
                             on_delete=models.CASCADE,
                             default="", blank=True, null=True)
