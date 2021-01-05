# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,BaseUserManager, PermissionsMixin)
from django.utils import timezone
from django.utils.translation import pgettext_lazy

class UserManager(BaseUserManager):

    def create_user(
            self, email, password=None, is_staff=False, is_active=True,
            **extra_fields):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop('username', None)

        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields)
            
    def staff(self):
        return self.get_queryset().filter(is_staff=True)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):

    first_name=models.CharField(max_length=255,blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    username = models.CharField(max_length=256, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    profile_image = models.FileField(upload_to='users', blank=True)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(('email'), unique=True, blank=False)  # changes email to unique and blank to false
    is_new = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        permissions = (
            (
                'manage_users', pgettext_lazy(
                    'Permission description', 'Manage customers.')),
            (
                'manage_staff', pgettext_lazy(
                    'Permission description', 'Manage staff.')),
            )

    def __str__(self):
        return self.first_name + " " + self.last_name


