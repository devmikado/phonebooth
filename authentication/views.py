# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
# from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse, JsonResponse
from .forms import LoginForm, SignUpForm
from .models import User
from social_django.models import UserSocialAuth


from b2b.models import customer_management, canned_response_management

from django.contrib.auth import views as django_views

from .decorators import type_wise_user_redirect

from .filters import CannnedFilter
from .utils import get_paginator_items
from django.conf import settings
import requests

from django.views.generic import TemplateView

@type_wise_user_redirect
def login_view(request):
    print(request.method)
    form = LoginForm(request.POST or None)
    msg = None
    try:
        if request.method == "POST":
            if form.is_valid():
                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")
                print(email)
                print(password)
                user = authenticate(email=email, password=password)
                print("/////////////////////////////////////")
                if user is not None:
                    if user.is_superuser:
                        login(request, user)
                        return redirect("/nationality/dashboard/")
                    else:
                        login(request, user)
                        social_logins = UserSocialAuth.objects.filter(user=request.user)
                        if social_logins:
                            return redirect("/customer/customer-dashboard/")
                        else:
                            return redirect('/customer/social-accounts/')
                else:
                    msg = 'Invalid credentials'
                    return render(request, "accounts/login.html", {"form": form, "msg": msg})
                
            else:
                print("==============================================>")
                print(form.errors)
                msg = 'Error validating the form'
        else:
            print("00000000000000000000000000000000000")
    except Exception as e:
        print("------------------e---------------------->")
        print(e)

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})


def register_user(request):
    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=raw_password)
            
            # create customer 
            customer_management.objects.create(user=user)
            
            msg     = 'User created.'
            success = True
            # messages.success(request, msg)

        else:
            print(form.errors)
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success" : success })


def logout_view(request):
    logout(request)
    return redirect('/')
    # Redirect to a success page.

def social_auth_login(request, backend):
    """
        This view is a wrapper to social_auths auth
        It is required, because social_auth just throws ValueError and gets user to 500 error
        after every unexpected action. This view handles exceptions in human friendly way.
        See https://convore.com/django-social-auth/best-way-to-handle-exceptions/
    """
    from social_auth.views import auth

    try:
        # if everything is ok, then original view gets returned, no problem
        return auth(request, backend)
    except ValueError as error:
        # in case of errors, let's show a special page that will explain what happened
        return render_to_response('users/login_error.html',
                                  locals(),
                                  context_instance=RequestContext(request))



def table(request):
    canned_responses = canned_response_management.objects.filter(customer_name__user=request.user).order_by("-id")
    
    canned_responses_filter = CannnedFilter(request.GET, queryset=canned_responses)
    
    canned_responses = get_paginator_items(
        canned_responses_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    
    print(canned_responses_filter)
    ctx  = {
        "canned_responses" : canned_responses,
        'filter_set': canned_responses_filter,
        'is_empty': not canned_responses_filter.queryset.exists()
    }
    return render(request, "table/sample.html", ctx)




# remember to install requests library using pip
def autoComplete(request):
    searchText = request.POST.get("req")
    depth = 2
    fanout = 2
    ts = 1575472870946
    showEmojisHashtags = "true"
    api_key = settings.AUTOCOMPLETE_API_KEY
    end_user_id = "woofy_dev_user"

    # defining the api-endpoint
    API_ENDPOINT = settings.AUTOCOMPLETE_API_ENDPOINT

    # sending post request and saving response as response object
    params = {
            'api_key': api_key,
            'searchText': searchText,
            'fanOut': fanout,
            'depth': depth,
            'ts': ts,
            'showEmojisHashtags': showEmojisHashtags,
            'end_user_id': end_user_id,
            'personal_dict': ["cat","dearly"],
            }
    resp = requests.post(url=API_ENDPOINT, json=params)

    # printing response
    keys = []
    msg_list = []
    emoji = []

    print(resp)
    if resp.status_code == 200:
        status = 1
        response = resp.json()
    
        if response['w_lm'] is not None:
            if response['w_lm']['suggestions']:
                suggestions = response['w_lm']['suggestions']
                for key in suggestions:
                    keys.append(key)

                for i in sorted(keys):
                    msg_list.extend(suggestions[i])
        else:
            msg_list = []
        keys = []
        if response['b_lm'] is not None:
            if response['b_lm']['suggestions']:
                suggestions = response['b_lm']['suggestions']
                for key in suggestions:
                    keys.append(key)

                for i in sorted(keys):
                    msg_list.extend(suggestions[i])

            
            if response['b_lm']['emoji_recos']:
                emoji = response['b_lm']['emoji_recos']
                # msg_list.append(emoji)

        if msg_list:
            res = {
                "message": msg_list,
                "short_message": msg_list[0],
                "emoji": emoji,
                "status": status
            }
        else:
            res = {
                
            }

        return JsonResponse(res)

    else:
        status = 2
        if resp:
            res = {
                "message": resp.json(),
                "status": status
            }
        else:
            res = {
                "message": "limit exceeds",
                "status": status
            }


        return JsonResponse(res)

from instagram.client import InstagramAPI
def get_instagram_access_token(code):
    short_live_access_token_url = "https://api.instagram.com/oauth/access_token"
    data = {
        'client_id': "603630760276200",
        'client_secret': "49c0abb6c647cb08cb4238e2d36266ef",
        'grant_type': 'authorization_code',
        'redirect_uri': "https://phoneboothb2b.progfeel.co.in/social-auth/complete/instagram/",
        'code': code
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    req = requests.post(short_live_access_token_url, data=data, headers=headers).json()
  
    return req
# 
    
def socialAuth(request):
    auth_code = ''
    data = {}
    if 'code' in request.GET:      
        # auth_code = request.GET.get('code').split('"')
        auth_code = request.GET.get('code')
        access_json = get_instagram_access_token(auth_code)
        try:
            user = User.object.get(id=request.user.id)
        except Exception as e:
            print(e)
            user = None

        if 'code' not in access_json:
            data =  {
                'extra_data': access_json,
                'user': request.user,
                'uid': str(access_json['user_id']),
                'provider': 'instagram'
            }
            exists = UserSocialAuth.objects.filter(uid=str(access_json['user_id']))
            if not exists:
                print("------------------if-1-221--------------------")
                user_social_auth = UserSocialAuth.objects.create(**data)
            else:
                print("------------------else-1---------------------")
                user_social_auth = exists.get(uid=access_json['user_id'])
                # user_social_auth.extra_data = access_json
                # user_social_auth.save()
                # user_social_auth.extra_data = access_json
                # user_social_auth.save()
            
            
            
            if user_social_auth:
                t = "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=49c0abb6c647cb08cb4238e2d36266ef&access_token="+access_json['access_token']+""

                d = requests.get(t).json()
                try:
                    get_profile = "https://graph.instagram.com/me?fields=id,username&access_token="+d['access_token']
                    profile = requests.get(get_profile).json()
                    d['username'] = profile['username']
                    d['user_id'] = profile['id']

                except Exception as e:
                    print(e)
                

                user_social_auth.extra_data = d
                user_social_auth.save()
                print("------------------if-2---------------------")
                return redirect('/customer/social-accounts/')
        else:
            data = "ok"
            return HttpResponse("auth_code")


class fastTextTraining(TemplateView):
    def createFastText(request):
        import csv
        import re

        train = open('phonebooth.train', 'w')
        test = open('phonebooth.valid', 'w')
        with open('ml_training.csv', mode='r', encoding="ISO-8859-1") as csv_file:
            csv_reader = csv.DictReader(csv_file, fieldnames=['target', 'id', 'date', 'flag', 'user', 'text'])
            line = 0
            for row in csv_reader:
                print(row)
                # Clean the training data
                # First we lower case the text
                text = row["text"].lower()
                # remove links
                text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text)
                # Remove usernames
                text = re.sub('@[^\s]+', '', text)
                # replace hashtags by just words
                text = re.sub(r'#([^\s]+)', r'\1', text)
                # correct all multiple white spaces to a single white space
                text = re.sub('[\s]+', ' ', text)
                # Additional clean up : removing words less than 3 chars, and remove space at the beginning and teh end
                text = re.sub(r'\W*\b\w{1,3}\b', '', text)
                text = text.strip()
                line = line + 1
                # Split data into train and validation
                if line % 16 == 0:
                    print('__label__{} {}'.format(row["target"],text), file=test)
                else:
                    print('__label__{} {}'.format(row["target"],text), file=train)

        return HttpResponse("Okay........")


def webhook(request):
    try:
        # 
        print("=============request.POST===============?")
        print(request.POST.get('hub_verify_token'))
        return HttpResponse(request.POST.get('hub_verify_token'))
        # challenge = request.POST.get('challenge')
        # verify_token = request.POST.get('hub_verify_token')
        # print("-------------verify-token-------------->")
        # print(verify_token)
        # if (verify_token == 'phonebooth'):
        #     return HttpResponse(challenge)
        # else:
        #     return HttpResponse("False")
    except Exception as e:
        print("------------e------------------>")
        print(e)