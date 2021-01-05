from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from social_django.models import UserSocialAuth
import random
# from .utils import get_instagram_access_token
from django.conf import settings
import requests
import json
from django.contrib import messages

def get_instagram_access_token(code):
    short_live_access_token_url = "https://api.instagram.com/oauth/access_token"
    
    data = {
        'client_id': settings.SOCIAL_AUTH_INSTAGRAM_KEY,
        'client_secret': settings.SOCIAL_AUTH_INSTAGRAM_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.SOCIAL_AUTH_INSTAGRAM_REDIRECT_URL,
        'code': code
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    req = requests.post(short_live_access_token_url, data=data, headers=headers).json()
    print("----------req------------------>")
    print(req)
    

    return req


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):

        print("@@@@@@@@@@@@@@@@@@@@@@@@ RAHUL @@@@@@@@@@@@@@@@@@@@@@@@")
        print('AT IN 38 middleware.py')
        print("@@@@@@@@@@@@@@@@@@@@@@@@ RAHUL @@@@@@@@@@@@@@@@@@@@@@@@")

        if hasattr(social_exceptions, 'AuthCanceled'):
            # return redirect('auth_login')
            print("------------------dd-------------------------->")
            print(exception)
            return redirect('/customer/social-accounts/')
            # return HttpResponse(exception)
        else:
            return HttpResponse(exception)

class MySocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        try:
            print("------------------request--------------------->")
            print(request.GET)
            data = {'denied_scopes': [''], 'code': ['AQBb9I18CzjK0qOKSvnThID5TQgCNqtYOE7bCjhaelMcFddK2o9d8d_GcFVvQsiWxzrQacN8We0nDBxn14iaahotq9-AP6hBWGtRdmjOF7LkZVfpXATiKJ4ftWfEnZpt1x8e6gsoG5EoYeinNS65EJtyVyKfuyrD3IGSsQhemIxh4QyT-R5xThmwYluUG8ZgK0nu0-PuZcKrM3TTqVx1DffRClmshoKc9kaKnCRHUvhXX8mg7icLvo37EYadShv_iCdjy9gAxD8XI0l3uOV5d_fXLt64whl5aO49k145vEcV_-BHRomFqqugiRuOwo-Ds8sIuAJM0o3oDKZ851-AN8hwqJCF5h4vX7YR23TKV-d29A'], 'state': ['QlfExwLX5xHr4YFclC1Q4GA6ulr3Nd9v'], 'granted_scopes': ['email,public_profile']}
            html = "<br><p><a href='/customer/social-accounts/'>Click here to go back to dashboard.</a><p>"
            if 'code' in data:      
                # auth_code = request.GET.get('code').split('"')
                auth_code = data['code']
                access_json = get_instagram_access_token(auth_code[0])
                print("---------------------------access_json---------------")
                print(access_json)
                if 'code' not in access_json:
                    
                    # t = "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret="+settings.SOCIAL_AUTH_INSTAGRAM_SECRET+"&access_token="+access_json['access_token']+""

                    # d = requests.get(t).json()
                    # print("---------------sss------dd-------------------")
                    # print(d)
                    

                    data =  {
                        'extra_data': access_json,
                        'user': request.user,
                        'uid': access_json['user_id'],
                        'provider': 'instagram'
                    }

                        
                   
                    exists = UserSocialAuth.objects.filter(uid=access_json['user_id'])
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
                        t = "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret="+settings.SOCIAL_AUTH_INSTAGRAM_SECRET+"&access_token="+access_json['access_token']+""

                        d = requests.get(t).json()
                        print("---------------sss------dd-------------------")
                        print(d)
                        user_social_auth.extra_data = d
                        user_social_auth.save()
                        print("------------------if-2---------------------")
                        return redirect('/customer/social-accounts/')
                else:
                    print("------------------else-2---------------------")
                    print(access_json)
                    msg = "OAuthException: Something Went Wrong! Please login after sometime."
                    
                    # return render(request, "customer/social/social_media.html", {"msg": msg})
                    messages.success(request, exception)
                    return redirect('/customer/social-accounts/')
            else:
                print("------------------else-3---------------------")
                # return HttpResponse(str(exception) + html)
                # pass
                msg = "Account Disconnected"
                messages.success(request, exception)
                return redirect('/customer/social-accounts/')

        except Exception as e:
            print("--------------exception--------------------->")
            print(e)
            return HttpResponse(e)
            # return redirect('/customer/social-accounts/')


from .models import User
from b2b.models import customer_management, fb_is_page_management

import facebook
def save_profile(backend, user, response, *args, **kwargs):

    try:

        print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        import random
        User.objects.filter(email='walter@yopmail.com').update(
            first_name=random.random()
        )

        print(UserSocialAuth.objects.filter(user=user).values_list('id'))

        a = UserSocialAuth.objects.filter(user=user).values('id', 'extra_data')
        for account in a:

            graph = facebook.GraphAPI(access_token=account['extra_data']['access_token'])
            pages_data = graph.get_object("/me/accounts")

            customer = customer_management.objects.get(user=user)

            added_Accout = []
            for item in pages_data['data']:
                accountx = UserSocialAuth.objects.get(id=account['id'])

                yx = fb_is_page_management.objects.filter(
                    customer_name=customer, fb_account=accountx, page_id=item['id']
                )

                added_Accout.extend(list(yx.values_list('id', flat=True)))

            tp = fb_is_page_management.objects.filter(
                customer_name=customer
            )

        print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')

        pass

    except:

        pass

