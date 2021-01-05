from django.db import models
from authentication.models import User
from social_django.models import UserSocialAuth

# Create your models here.
class connectedSocialAccount(models.Model):
    social_account = models.CharField(max_length=255, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.social_account


class FreeListeningFIlter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    countries = models.CharField(max_length=255, null=True, blank=True)
    cities = models.CharField(max_length=255, null=True, blank=True)
    hashtags = models.CharField(max_length=255, null=True, blank=True)
    cultures = models.CharField(max_length=255, null=True, blank=True)

    def __int__(self):
        return self.id 
