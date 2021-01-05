# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', login_view, name="login"),
    path('register/', register_user, name="register"),
    # path("logout/", LogoutView.as_view(), name="logout")
    path('logout/', logout_view, name='logout'),
    path('table/', table, name='table'),
    url(r'^social_auth_login/([a-z]+)$',  social_auth_login, name='users-social-auth-login'), 


    # forgot password

    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),


    # auto complete api
    path("api/auto-complete/", autoComplete, name="auto-complete"),

    path("social-auth/complete/instagram/", socialAuth, name="social-auth"),
    path("code/", get_instagram_access_token),

    path("fasttext/", fastTextTraining.createFastText),
    
    path("webhook/", webhook, name="webhook"),
]
