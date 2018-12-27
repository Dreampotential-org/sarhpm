from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=17, blank=True)

    def __str__(self):
        return self.user.username
