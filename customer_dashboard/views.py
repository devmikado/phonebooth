from django.shortcuts import render

# Create your views here.
from authentication.models import UserManager
from .forms import RegistrationForm, LoginForm,UserProfileForm, CustomerForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect

from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.utils import timezone
from phonebooth.decorators import is_superuser
from django.contrib import messages
import requests

import json
# social auth model
from social_django.models import UserSocialAuth
from dateutil import parser
from django.contrib.auth.decorators import login_required
# from .decorators import login_required

# models
from authentication.models import User
from b2b.models import *
from nationality.models import *
from nationality.models import *
from .models import *
from django.conf import settings
from django.db.models import Q

import sys
import json
import time
import logging
import twitter
import urllib.parse

from os import environ as e
from geopy import geocoders  
from geopy.geocoders import Nominatim

# social apps
from langdetect import detect
from textblob import TextBlob
from iso639 import languages

# from .tasks import get_tweets_for_user
from celery import shared_task

# instagram
from instagram.client import InstagramAPI

# cron
import facebook

from .utils import get_facebook_comment

from .models import connectedSocialAccount
import ast
from django.db.models import Count, Sum


def login_view(request):
    print("------------------------------------------>")
    print(request.user)

    if not request.user.is_anonymous:
        return redirect("/dashboard/")
    else:
        form = LoginForm(request.POST or None)
        msg = None

        if request.method == "POST":

            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)

            else:
                msg = 'Error validating the form'

        return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'User created.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = RegistrationForm()
    print("-------------------------------------->")
    print(form)

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })



# @is_superuser
def customer_dashboard(request):
    context = {}
    twCommentanswered = 0
    twCommentPositive = 0
    twCommentNegative = 0
    fbComment = 0
    instaComment = 0
    user = request.user
    try:
        customerObj = customer_management.objects.get(user=request.user)
        social_accounts = UserSocialAuth.objects.filter(user=request.user)
        twPostObj = twitter_post_management.objects.filter(customer_name=customerObj)
        customerPersonaObj = customer_persona.objects.filter(user=request.user).all().order_by('-id')
        reportTypeObj = ReportTypeMaster.objects.all()

        fbCommentObj = fb_comment_management.objects.filter(customer_name=customerObj, is_replied=False)
        fbCommentunanswered = fbCommentObj.count()

        # for postObj in twPostObj:
        twCommentObj = twitter_comment_management.objects.filter(customer_name=customerObj, is_replied=False)    
        twCommentunanswered = twCommentObj.count()

        twCommentObjpositive = twitter_comment_management.objects.filter(customer_name=customerObj, sentiment=1)
        twCommentPositive = twCommentObjpositive.count()

        twCommentObjnegative = twitter_comment_management.objects.filter(customer_name=customerObj, sentiment=2)
        twCommentNegative = twCommentObjnegative.count()

        instaComment = ig_comment_management.objects.filter(customer_name=customerObj, is_replied=False)
        instaCommentunanswered = instaComment.count()
    

        context = {
            'fbcomment': fbCommentunanswered,
            'twComment': twCommentunanswered,
            'twCommentpositive': twCommentPositive,
            'twCommentnegative': twCommentNegative,
            # 'fbComment': fbComment,
            'instaComment' : instaCommentunanswered,
            "social_accounts": social_accounts,
            'customerPersonaObj': customerPersonaObj,
            'reportTypeObj':reportTypeObj,
            'customer_id': customerObj.id
        }

        print(context)
    except Exception as e:
        print("------------------context-exception------------------>")
        print(e)
    if request.user.is_superuser == True:
        return redirect("/customer/customers-list/")
    else:
        return render(request, 'customer/index.html', context)


from instagram import client

class SocialMediaPlatform(TemplateView):
    # @login_required
    def tweet_url(t):
        return "https://twitter.com/%s/status/%s" % (t.user.screen_name, t.id)

    def get_replies(customer, tweet):
        twitter_access_token_key = ''
        access_token_secret = ''
        try:
            customer = customer
            print(customer)
        except Exception as e:
            print("=======================================>")
            print(e)
        twitter_credentials = UserSocialAuth.objects.filter(user=customer.user, provider='twitter')
        # twitter_credentials = UserSocialAuth.objects.filter(id=37)
        for account in twitter_credentials:
            twitter_access_token_key = account.extra_data['access_token']['oauth_token']
            access_token_secret = account.extra_data['access_token']['oauth_token_secret']
        t = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                    consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                    access_token_key=twitter_access_token_key,
                    access_token_secret=access_token_secret,
                    sleep_on_rate_limit=True)

        user = tweet.user.screen_name
        tweet_id = tweet.id
        max_id = None
        logging.info("looking for replies to: %s" % SocialMediaPlatform.tweet_url(tweet))
        while True:
            q = urllib.parse.urlencode({"q": "to:%s" % user})
            try:
                replies = t.GetSearch(raw_query=q, since_id=tweet_id, max_id=max_id, count=100)
            except twitter.error.TwitterError as e:
                logging.error("caught twitter api error: %s", e)
                time.sleep(60)
                continue
            for reply in replies:
                if reply.in_reply_to_status_id == tweet.id:
                    try:
                        twPostManagementObj = twitter_comment_management.objects.get(tweet_reply_id=reply.in_reply_to_status_id)
                        twPostManagementObj.resposne_sent = reply.text
                        twPostManagementObj.is_replied = True
                        twPostManagementObj.save()
                    except Exception as e:
                        print(e)
               
                  
                max_id = reply.id
            
            if len(replies) != 100:
                break

    def get_sentiment(message):
        import fasttext
        from django.db.models import Q
        model = fasttext.load_model("phonebooth.bin")
        print("------------------input-------------------->")
        print(message)
        sentimentData = model.predict(str(" ".join(message.split())), k=3)
        print(sentimentData)
        if sentimentData[0][0] == "__label__0":
            sentiment = "negative"
        elif sentimentData[0][0] == "__label__2":
            sentiment = "neutral"
        elif sentimentData[0][0] == "__label__4":
            sentiment = "positive"
        else:
            sentiment = "neutral"
        print("------------------output-------------------->")
        print(sentiment)
        return sentiment

    def get_nationality(status):
        import requests
        payload = {}
        headers = {}
        
        # user = api.UsersLookup(screen_name=screen_name)
        # # print(user)
        # for i in user:
        #     print(i)
        name = status.user.name.split(" ")
        if len(name) > 1:
            first_name = status.user.name.split(" ")[0]
            last_name = status.user.name.split(" ")[1]
        else:
            first_name = status.user.name.split(" ")[0]
            last_name = ''

        if last_name != "":
            forebears_url = 'https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+first_name+'&sn='+last_name+'&sanitise=1'
        else:
            forebears_url = 'https://ono.4b.rs/v1/nat?key=' + settings.FOREBEARS_KEY + '&fn=' + first_name + '&sn=""&sanitise=1'
  
        response = requests.request("GET", forebears_url, headers=headers, data=payload)
        responseData = response.json()

        if 'countries' in responseData:
            nationality = responseData['countries'][0]
        else:
            nationality = None
        return nationality
  

    @login_required
    def socialmdedia(request):

        # debug line : Rahul M [14-Oct-2020]

        # import random
        # User.objects.filter(email='walter@yopmail.com').update(
        #     first_name=random.random()
        # )

        # debug line : Rahul M [14-Oct-2020]


        fbaccountList = []
        instaaccountList = []
        twitteraccountList = []
        fb_connection = None
        insta_count = 0
        


        try:
            customer = customer_management.objects.get(user=request.user)
        except Exception as e:
            print(e)
            customer = None
        try:
            fb_connection = connectedSocialAccount.objects.filter(user=request.user).order_by("-id")[0]
            
            latest_social_entry = UserSocialAuth.objects.filter(user=request.user).order_by("-id")[0]

            # if fb_connection and latest_social_entry:
            #     if fb_connection.social_account == latest_social_entry.provider:
            #         pass
            #     else:
            #         latest_social_entry.provider = fb_connection.social_account
            #         latest_social_entry.save()
            # else:
            #     pass
            #     # twitter_accounts_count = UserSocialAuth.objects.filter(user=request.user, provider='twitter')

        except Exception as e:
            print(e)

        facebook_accounts_count = UserSocialAuth.objects.filter(user=request.user, provider='facebook')

        instagram_accounts_count = UserSocialAuth.objects.filter(user=request.user, provider='instagram')

        twitter_accounts_count = UserSocialAuth.objects.filter(user=request.user, provider='twitter')

        from .utils import get_social_account_details
        get_social_account_details(request.user)

        if fb_connection:
            fb_accounts = UserSocialAuth.objects.filter(user=request.user, provider='facebook').values('id','extra_data')

            

            if fb_accounts:
                responseDict = {}
                for account in fb_accounts:
                    graph = facebook.GraphAPI(access_token=account['extra_data']['access_token'])  
                    # to get page data
                    pages_data = graph.get_object("/me/accounts")

                    for item in pages_data['data']:
                        try:
                            fb_ac = UserSocialAuth.objects.get(user=request.user, id=account['id'])
                        except Exception as e:
                            fb_ac = None

                        fb_page_exists = fb_is_page_management.objects.filter(customer_name=customer, fb_account=fb_ac, page_id=item['id'])
                        
                        if not fb_page_exists:
                            is_page_removed = removed_fb_page_details.objects.filter(page_id=item['id'], fb_account=fb_ac)
                            
                            if not is_page_removed: 
                                fb_page_management = fb_is_page_management.objects.create(customer_name=customer,
                                user_access_token=account['extra_data']['access_token'], page_access_token=item['access_token'], page_name=item['name'], page_id=item['id'], fb_account=fb_ac)
                                fb_page_management.save()
                            else:
                                pass
                        else:
                            pass
                    
                    fb_pages = fb_is_page_management.objects.filter(fb_account=account['id'], customer_name=customer).values('id', 'page_name')
                    for page in fb_pages:
                        responseDict[page['id']] = account['extra_data']['name'] + " - "+ page['page_name']
                    
                fbaccountList.append(responseDict)

        if instagram_accounts_count:
            print("-------------if-1--------------------------->")
            insta_accounts = UserSocialAuth.objects.filter(user=request.user, provider='instagram').values('id', 'extra_data')
            
            if insta_accounts:
                print("-------------if-2--------------------------->")
                responseDict = {}
                for account in insta_accounts:
                    # get pages
                    graph = facebook.GraphAPI(access_token=account['extra_data']['access_token'])
                    # to get page data
                    pages_data = graph.get_object("/me/accounts")
                    print(pages_data)
                    for item in pages_data['data']:
                        print("--------------for-1--------------------->")
                        try:
                            fb_ac = UserSocialAuth.objects.get(user=request.user, id=account['id'])
                            
                        except Exception as e:
                            print(e)
                            fb_ac = None

                        fb_page_exists = fb_is_page_management.objects.filter(customer_name=customer, fb_account=fb_ac, page_id=item['id'])
                        print("-------------if-3--------------------------->")
                        print(fb_page_exists)
                        if not fb_page_exists:
                            print("-------------if-3--------------------------->")
                            is_page_removed = removed_fb_page_details.objects.filter(page_id=item['id'], fb_account=fb_ac)
                            if not is_page_removed:
                                print("-------------if-4--------------------------->")
                                fb_page_management = fb_is_page_management.objects.create(customer_name=customer,
                                user_access_token=account['extra_data']['access_token'], page_access_token=item['access_token'], page_name=item['name'], page_id=item['id'], fb_account=fb_ac)
                                fb_page_management.save()
                            else:
                                pass
                        else:
                            print("-------------else-1---------------------->")
                            fb_page_management = fb_is_page_management.objects.filter(customer_name=customer, fb_account=fb_ac, page_id=item['id'])

                    
                    
                    fb_pages = fb_is_page_management.objects.filter(fb_account__id=account['id'], customer_name=customer)


                    
                    for page in fb_pages:
                        insta_count += 1
                        print('___________________ IN INSTA _________________')
                        # print(page.id)

                        get_insta_id = "https://graph.facebook.com/"+page.page_id+"?fields=instagram_business_account&access_token="+page.user_access_token


                        print('URL --> '+str(get_insta_id))
                      
                        insta_id = requests.get(get_insta_id).json()
                        print(insta_id)

                        if 'instagram_business_account' in insta_id:
                            instagram_business_id = insta_id['instagram_business_account']

                            # remove_fb_page = fb_is_page_management.objects.filter(fb_account__id=account['id'], customer_name=customer).exclude(page_id=insta_id['id']).delete()
                            
                            if instagram_business_id:
                                get_username = "https://graph.facebook.com/"+instagram_business_id['id']+"?fields=username&access_token=" + page.user_access_token

                                username = requests.get(get_username).json()
                                
                                # try:
                                #     user_profile = "https://www.instagram.com/"+username['username']+"/?__a=1"


                                #     user_profile_data = requests.get(user_profile).json()
                                #     user_name = user_profile_data['graphql']['user']['full_name']
                                # except Exception as e:
                                #     print(e)

                            responseDict[page.id] = username['username']
                        else:
                            page.delete()
                instaaccountList.append(responseDict)

                print("==============instaaccountList=====================>")
                print(instaaccountList)
        

        twiiter_accounts = twitter_accounts_count.values('id','extra_data')
        
        if twiiter_accounts:
            twitteraccountList = []
            responseDict = {}
            for account in twiiter_accounts: 
                responseDict[account['id']] = account['extra_data']['access_token']['screen_name']
            
            twitteraccountList.append(responseDict)

        unauthenticated_api = client.InstagramAPI(client_id=settings.SOCIAL_AUTH_INSTAGRAM_KEY, client_secret=settings.SOCIAL_AUTH_INSTAGRAM_SECRET,redirect_uri=settings.SOCIAL_AUTH_INSTAGRAM_REDIRECT_URL)
        try:
            url = unauthenticated_api.get_authorize_url(scope=["user_profile","user_media"])
            # return render(request, 'app/login.html', {'url': url})
        except Exception as e:
            print(e)

        social_logins = UserSocialAuth.objects.filter(user=request.user)
        if social_logins:
            new_user = "False"
        else:
            new_user = "True"

        facebook_pages_count = fb_is_page_management.objects.filter(fb_account__user=request.user, fb_account__provider='facebook', customer_name=customer)    

        instagram_accounts_count = fb_is_page_management.objects.filter(fb_account__provider='instagram', fb_account__user=request.user)  

        context = {
            'facebook_accounts_count': facebook_accounts_count.count(),
            'instagram_accounts_count': instagram_accounts_count.count(),
            'twitter_accounts_count': twitter_accounts_count.count(),
            'facebook_pages_count': facebook_pages_count.count(),

            'twitter_accounts': twitteraccountList,
            'fb_accounts': fbaccountList,
            'insta_account': instaaccountList,
            "url": url,
            "new_user": request.user.is_new,
            "user_id": request.user.id

        }
       
        return render(request, 'customer/social/social_media.html',{'context': context})


class customerListView(ListView):

    model = User
    paginate_by = 10  # if pagination is desired
    template_name = 'customer/customer_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class customerDetailView(DetailView):

    model = User
    template_name = 'customer/customer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class customerReportView(ListView):

    model = User
    template_name = 'customer/customer_reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def user_profile(request, id):
    msg = None
    context = {}
    print("-------------------------------------->")
    print(id)

    # personal info
    try:
        user = User.objects.get(id=id)
        
    except Exception as e:
        user = User()
        
    # business info
    try:
        customer = customer_management.objects.get(user=user)
    except:
        customer = customer_management()



    form = UserProfileForm(request.POST or None, instance = user)
    customer_form = CustomerForm(request.POST or None, instance = customer)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance = user)
        customer_form = CustomerForm(request.POST, request.FILES, instance = customer)

        if form.is_valid() and customer_form.is_valid():
            form.save()
            customer_form.save()
           
            msg     = 'User Profile Updated Successfully'
            messages.success(request, msg)
            return redirect("/")
            

        else:
            print(form.errors)
            msg = 'Form is not valid'
  
    context = {
        "customer_form": customer_form,
        "form": form,
        "user": user,
        "customer": customer
    }

    return render(request, "customer/profile.html", context)


def socialAccount(request):
    # print(request.POST)
    # <QueryDict: {'social_account': ['Instagram'], 'user_id': ['2']}>
    social_account = request.POST.get("social_account")
    user_id = request.POST.get("user_id")
    connectedSocialAccount.objects.create(social_account=social_account, user_id=user_id)
    return HttpResponse("ok")


class CustomerDashboard(TemplateView):
    @login_required
    def customer_dashboard(request):
        # getInstaFeeds(request)
        customer = None
        twitter_access_token_key = ''
        access_token_secret = ''
        try:
            customer = customer_management.objects.get(user=request.user)
            print(customer)
        except Exception as e:
            print("=======================================>")
            print(e)
        
        return customer_dashboard(request)


def on_login(request):
    unauthenticated_api = InstagramAPI(client_id=settings.SOCIAL_AUTH_INSTAGRAM_KEY, client_secret=settings.SOCIAL_AUTH_INSTAGRAM_SECRET,redirect_uri=settings.SOCIAL_AUTH_INSTAGRAM_REDIRECT_URL)
    # unauthenticated_api = InstagramAPI(**settings.INSTAGRAM_CONFIG)
    try:
        redirect_uri = unauthenticated_api.get_authorize_url(scope=["user_profile","user_media"])
        print(redirect_uri)
    except Exception as e:
        print(e)

def connectInstagram(request):
    unauthenticated_api = InstagramAPI(client_id=settings.SOCIAL_AUTH_INSTAGRAM_KEY, client_secret=settings.SOCIAL_AUTH_INSTAGRAM_SECRET,redirect_uri=settings.SOCIAL_AUTH_INSTAGRAM_REDIRECT_URL)
    # unauthenticated_api = InstagramAPI(**settings.INSTAGRAM_CONFIG)
    try:
        redirect_uri = unauthenticated_api.get_authorize_url(scope=["user_profile","user_media"])
        return JsonResponse({"url": redirect_uri})
    except Exception as e:
        print(e)
    


def feed_comment(api, customer, status):
    try:
        twitter_obj = None
        twitReplyObj = twitter_post_management.objects.filter(customer_name=customer, tweet_id=status.in_reply_to_status_id)
        
        if twitReplyObj:
            for i in twitReplyObj:
                twitter_obj = i

        if twitter_obj != None:
            try:
                alreay_exists = twitter_comment_management.objects.filter(message=status.text,tweet_reply_id=status.id)
                if not alreay_exists:
                    twPostManagementObj = twitter_comment_management(customer_name=customer,created_time=parser.parse(status.created_at),message=status.text,tweet_reply_id=status.id,twitter_post_ref=twitter_obj)

                    twPostManagementObj.save()

            

                # get sentiment
                sentiment = SocialMediaPlatform.get_sentiment(twPostManagementObj.message)
                    
                # get nationality
                nationality = SocialMediaPlatform.get_nationality(status)
                if nationality:
                    twPostManagementObj.nationality = nationality['jurisdiction']
                    twPostManagementObj.nationality_percent = nationality['percent']

                # get language of comment
                # lang = detect(status.text)
                # lang = Translator(status.text)
                blob = TextBlob(status.text)
                l = languages.get(alpha2=blob.detect_language())
                lang = l.name
                twPostManagementObj.comment_language = lang

                if status.user.location:
                    geolocator = Nominatim(user_agent='myapplication')
                    location = geolocator.geocode(status.user.location)
                    if location.raw:
                        location_lat = location.raw['lat']
                        location_lon = location.raw['lon']
                        location = location.raw['display_name']

                        twPostManagementObj.location = location
                        twPostManagementObj.location_lat = location_lat
                        twPostManagementObj.location_lon = location_lon
                    else:
                        twPostManagementObj.location = location

                    twPostManagementObj.save()

            
                twPostManagementObj.save()
                        
                try:
                    sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                    twPostManagementObj.sentiment = sentiment
                    twPostManagementObj.save()
                except Exception as e:
                    print("888888888888888888888888888888888888")
                    print(e)
            
            except Exception as e:
                print(e)
        else:
            pass



    except Exception as e:
        print("-----------except-2----------")
        print(e)


# @shared_task
def get_tweets_for_user(request):
    status_id = []
    try:
        customers = customer_management.objects.filter(user__is_active=True).values_list('user_id', flat=True)

        twitter_credentials = UserSocialAuth.objects.filter(provider='twitter', user_id__in=customers)
        
        twitter_comment_management.objects.all().delete()
        if twitter_credentials:
            for account in twitter_credentials:
                try:
                    customer = customer_management.objects.get(user_id=account.user.id)
                except:
                    customer = None
                twitter_access_token_key = account.extra_data['access_token']['oauth_token']
                access_token_secret = account.extra_data['access_token']['oauth_token_secret']
                api = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                            consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                            access_token_key=twitter_access_token_key,
                            access_token_secret=access_token_secret,
                            sleep_on_rate_limit=True)
                
                # try:
                verifyData = api.VerifyCredentials()
                statuses = api.GetUserTimeline(screen_name=verifyData.screen_name, count=50)

                for status in statuses:
                    try:
                        if status.in_reply_to_status_id is None:
                            already_exist = twitter_post_management.objects.filter(tweet_id=status.id, twitter_account=account)
                            if already_exist:
                                pass
                            else:
                                twitterPostManagement = twitter_post_management     (customer_name=customer,
                                                created_time=parser.parse(
                                                status.created_at),
                                                message=status.text,
                                                tweet_id=status.id,
                                                twitter_account=account)
                            
                                twitterPostManagement.save()
                            
                    except Exception as e:
                        print(e)
                        
                for status in statuses:
                    twitter_obj = None
                    if status.in_reply_to_status_id is not None:
                        feed_comment(api, customer, status)
             
                    else:
                        logging.info("looking for replies to: %s" % SocialMediaPlatform.tweet_url(status))
                        user = status.user.screen_name
                        max_id = None
                        
                        q = urllib.parse.urlencode({"q": "to:%s" % user})
                        try:
                            replies = api.GetSearch(raw_query=q, since_id=status.id, max_id=max_id, count=100)
                        except twitter.error.TwitterError as e:
                            logging.error("caught twitter api error: %s", e)
                            time.sleep(60)
                            continue
                        
                        for reply in replies:
                            if reply.in_reply_to_status_id is not None:
                                if reply.in_reply_to_status_id not in status_id:
                                    status_id.append(reply.in_reply_to_status_id)
                                    feed_comment(api, customer, reply)
                                    
         
                
            return HttpResponse("ok")

    except Exception as e:
        print("----------final exception------------->")
        print(e)

    return HttpResponse("ok")
    

def get_social_account(request):
    responseList = []

    user_id = request.POST.get("user_id")
    social_accounts = UserSocialAuth.objects.filter(user_id=user_id).values('id', 'extra_data')
    for account in social_accounts:
        responseDict = {}
        responseDict["id"] = account['id']
        responseDict["name"] = account['extra_data']['access_token']['screen_name']
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)


def disconnect_social_account(request, pk, platform):
    responseList = []
    try:
        if platform == "facebook":
            fb_page = fb_is_page_management.objects.filter(customer_name__user=request.user)
            if fb_page.count() == 1:
                fb_page = fb_is_page_management.objects.get(id=pk)
                social_account = UserSocialAuth.objects.get(provider='facebook', id=fb_page.fb_account.id)
                social_account.delete()                
            fb_page = fb_is_page_management.objects.get(id=pk)
            
            removed_page = removed_fb_page_details.objects.create(
                page_name = fb_page.page_name,
                user_access_token = fb_page.user_access_token,
                page_access_token= fb_page.page_access_token,
                fb_account=fb_page.fb_account,
                page_id=fb_page.page_id

            )
            removed_page.save()
            fb_page.delete()

            msg = "Page Disconnected"
        else:
            social_account = UserSocialAuth.objects.get(id=pk)
            social_account.delete()
            msg = "Account Disconnected"
        messages.success(request, msg)


    except Exception as e:
        print(e)
    
    

    return JsonResponse({"success": 1, "message": "Deleted"})


def auth(request):
    print(request)
    return HttpResponse("ok")


def get_nationality(name):
        import requests
        payload = {}
        headers = {}
        
        # user = api.UsersLookup(screen_name=screen_name)
        # # print(user)
        # for i in user:
        #     print(i)
        name = name.split(" ")
        if len(name) > 1:
            first_name = name[0]
            last_name = name[1]
        else:
            first_name = name[0]
            last_name = ''

        if last_name != "":
            forebears_url = 'https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+first_name+'&sn='+last_name+'&sanitise=1'
        else:
            forebears_url = 'https://ono.4b.rs/v1/nat?key=' + settings.FOREBEARS_KEY + '&fn=' + first_name + '&sn=""&sanitise=1'
  
        response = requests.request("GET", forebears_url, headers=headers, data=payload)
        responseData = response.json()

        if 'countries' in responseData:
            nationality = responseData['countries'][0]
        else:
            nationality = None
        return nationality


def get_insta_reply(data, fb_access_token, instaPostManagement, instagram_business_id):
    print("--------------------------------------------------------->")
    # get replies
    url_insta_comments = "https://graph.facebook.com/v8.0/"+data['id']+"/replies?fields=id,text,user,timestamp&access_token="+fb_access_token

    comments_data = requests.get(url_insta_comments).json()
    
    if comments_data['data']:
        for data in comments_data['data']:
            print(data)
            if 'user' in data:
                print(instagram_business_id)
                if (data['user']['id'] == instagram_business_id):
                    print("DO nothing")
                    instaPostManagementObj = None
            else:
                try:
                    get_username = "https://graph.facebook.com/v8.0/"+data['id']+"?fields=username,user,replies&access_token="+fb_access_token

                    username = requests.get(get_username).json()

                    user_profile = "https://www.instagram.com/"+username['username']+"/?__a=1"
                    user_profile_data = requests.get(user_profile).json()
                    user_name = user_profile_data['graphql']['user']['full_name']

                except Exception as e:
                    print(e)
                    user_name = ''

                comment_alreay_exists = ig_comment_management.objects.filter(ig_comment_id=data['id'], message=data['text'])

                if comment_alreay_exists:
                    instaPostManagementObj = None
                else:
                    instaPostManagementObj = ig_comment_management.objects.create(
                        customer_name=instaPostManagement.customer_name,
                        ig_post_ref=instaPostManagement,
                        created_time=parser.parse(data['timestamp']),
                        message=data['text'],
                        ig_comment_id=data['id'],
                        commented_username=user_name
                    )
                    instaPostManagement.save()

            if instaPostManagementObj:
                # get sentiment
                sentiment = SocialMediaPlatform.get_sentiment(data['text'])

                # get nationality
                nationality = get_nationality(instaPostManagementObj.commented_username)
                if nationality:
                    instaPostManagementObj.nationality = nationality['jurisdiction']
                    instaPostManagementObj.nationality_percent = nationality['percent']

                # get language of comment
                # lang = detect(status.text)
                # lang = Translator(status.text)
            
                try:
                    blob = TextBlob(data['text'])
                    l = languages.get(alpha2=blob.detect_language())
                    lang = l.name
                except Exception as e:
                    print("-----except---------------------->")
                    print(e)
                    lang = ''
                instaPostManagementObj.comment_language = lang

                # if status.user.location:
                #     geolocator = Nominatim(user_agent='myapplication')
                #     location = geolocator.geocode(status.user.location)
                #     if location.raw:
                #         location_lat = location.raw['lat']
                #         location_lon = location.raw['lon']
                #         location = location.raw['display_name']

                #         twPostManagementObj.location = location
                #         twPostManagementObj.location_lat = location_lat
                #         twPostManagementObj.location_lon = location_lon
                #     else:
                #         twPostManagementObj.location = location

                #     twPostManagementObj.save()

                url_reply_on_comments = "https://graph.facebook.com/v8.0/"+instaPostManagementObj.ig_comment_id+"/replies?access_token="+fb_access_token

                reply_on_comment = requests.get(url_reply_on_comments).json()
                print("---------------reply_on_comment--------------->")
                print(reply_on_comment)

                if 'data' in reply_on_comment:
                    instaPostManagementObj.is_replied = True
            
                instaPostManagementObj.save()
                        
                try:
                    sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                    instaPostManagementObj.sentiment = sentiment
                    instaPostManagementObj.save()
                except Exception as e:
                    print("888888888888888888888888888888888888")
                    print(e)

                

def getInstaFeeds(request):
    try:
        instagram_business_id = ''
        try:
            customers = customer_management.objects.filter(user__is_active=True).values_list('user_id', flat=True)
        except Exception as e:
            print("--------------customer-e------------------>")
            print(e)
            customers = None

        social_accounts = UserSocialAuth.objects.filter(user_id__in=customers, provider = "instagram")
        # social_accounts = UserSocialAuth.objects.filter(user=request.user, provider="instagram")
        # ig_comment_management.objects.all().delete()
        if social_accounts:
            print("------------------if-1------------------>")
            for account in social_accounts:
                print(account.id)
                
                fb_access_token = account.extra_data['access_token']

                # get connected fb pages
                fb_pages = fb_is_page_management.objects.filter(fb_account=account)
                for page in fb_pages:
                    get_insta_id = "https://graph.facebook.com/"+page.page_id+"?fields=instagram_business_account&access_token="+fb_access_token
                    
                    insta_id = requests.get(get_insta_id).json()

                    if 'instagram_business_account' in insta_id:
                        instagram_business_id = insta_id['instagram_business_account']


                try:
                    customer = customer_management.objects.get(user_id=account.user.id)
                except:
                    customer = None

                if instagram_business_id:
                    print("------------------instagram_business_id1------------------>")
                    try:
                        instagram_business_id = instagram_business_id['id']
                    except Exception as e:
                        instagram_business_id = instagram_business_id

                    print(instagram_business_id)
                    url_get_media_id = "https://graph.facebook.com/"+instagram_business_id+"/media?access_token="+fb_access_token
            
                    get_media = requests.get(url_get_media_id).json()

                    if 'data' in get_media:
                        print("------------------if-3------------------>")
                        media_ids = get_media['data']
                        for media_id in media_ids:
                            user_get_media_data = "https://graph.facebook.com/"+media_id['id']+"?fields=id,media_type,media_url,username,timestamp,caption&access_token="+fb_access_token

                            get_media_data = requests.get(user_get_media_data).json()
                            

                            # ig_post_management
                            if get_media_data:
                                print("------------------if-4------------------>")
                                already_exist = ig_post_management.objects.filter(insta_account=account, ig_post_id=get_media_data['id'])
                                if already_exist:
                                    print("------------------if-5------------------>")
                                    instaPostManagement = ig_post_management.objects.get(insta_account=account, ig_post_id=get_media_data['id'])
                                else:
                                    print("-------------------else-1------------------>")
                                    print(get_media_data)
                                    msg = ''
                                    if 'caption' in get_media_data:
                                        print("-------------------if-6------------------>")
                                        msg = get_media_data['caption']
                                    instaPostManagement = ig_post_management.objects.create(
                                        customer_name=customer,
                                        created_time=parser.parse(get_media_data['timestamp']),
                                        message=msg,
                                        media_type= get_media_data['media_type'],
                                        media_url= get_media_data['media_url'],
                                        insta_account=account,
                                        ig_post_id=get_media_data['id']
                                    )
                                    instaPostManagement.save()

                            # get comments
                            url_insta_comments = "https://graph.facebook.com/v8.0/"+instaPostManagement.ig_post_id+"/comments?access_token="+fb_access_token
                            
                            comments_data = requests.get(url_insta_comments).json()
                        
                            if comments_data:
                                print("-------------------if-7------------------>")
                                for data in comments_data['data']:
                                    print(data)
                                    get_insta_reply(data, fb_access_token, instaPostManagement, instagram_business_id)
                                    try:
                                        get_username = "https://graph.facebook.com/v8.0/"+data['id']+"?fields=username,user,replies&access_token="+fb_access_token

                                        username = requests.get(get_username).json()

                                        user_profile = "https://www.instagram.com/"+username['username']+"/?__a=1"


                                        user_profile_data = requests.get(user_profile).json()
                                        user_name = user_profile_data['graphql']['user']['full_name']
                                    except Exception as e:
                                        print(e)
                                        user_name = ''
                                    
                                    comment_alreay_exists = ig_comment_management.objects.filter(ig_comment_id=data['id'], message=data['text'])
                                    
                                    if comment_alreay_exists:
                                        instaPostManagementObj = ig_comment_management.objects.get(ig_comment_id=data['id'], message=data['text'])
                                    else:
                                        instaPostManagementObj = ig_comment_management.objects.create(
                                            customer_name=customer,
                                            ig_post_ref=instaPostManagement,
                                            created_time=parser.parse(data['timestamp']),
                                            message=data['text'],
                                            ig_comment_id=data['id'],
                                            commented_username=user_name
                                        )
                                        instaPostManagement.save()

                                    # get sentiment
                                    sentiment = SocialMediaPlatform.get_sentiment(data['text'])

                                    # 
                                        
                                    # get nationality
                                    nationality = get_nationality(instaPostManagementObj.commented_username)
                                    if nationality:
                                        instaPostManagementObj.nationality = nationality['jurisdiction']
                                        instaPostManagementObj.nationality_percent = nationality['percent']

                                    # get language of comment
                                    # lang = detect(status.text)
                                    # lang = Translator(status.text)
                                
                                    try:
                                        blob = TextBlob(data['text'])
                                        l = languages.get(alpha2=blob.detect_language())
                                        lang = l.name
                                    except Exception as e:
                                        print("-----except---------------------->")
                                        print(e)
                                        lang = ''
                                    instaPostManagementObj.comment_language = lang

                                    # if status.user.location:
                                    #     geolocator = Nominatim(user_agent='myapplication')
                                    #     location = geolocator.geocode(status.user.location)
                                    #     if location.raw:
                                    #         location_lat = location.raw['lat']
                                    #         location_lon = location.raw['lon']
                                    #         location = location.raw['display_name']

                                    #         twPostManagementObj.location = location
                                    #         twPostManagementObj.location_lat = location_lat
                                    #         twPostManagementObj.location_lon = location_lon
                                    #     else:
                                    #         twPostManagementObj.location = location

                                    #     twPostManagementObj.save()

                                    url_reply_on_comments = "https://graph.facebook.com/v8.0/"+instaPostManagementObj.ig_comment_id+"/replies?access_token="+fb_access_token

                                    reply_on_comment = requests.get(url_reply_on_comments).json()

                                    if reply_on_comment['data']:
                                        instaPostManagementObj.is_replied = True
                                
                                    instaPostManagementObj.save()
                                            
                                    try:
                                        sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                                        instaPostManagementObj.sentiment = sentiment
                                        instaPostManagementObj.save()
                                    except Exception as e:
                                        print("8888888888888888888888888888888888888888")
                                        print(e)
                                        

            return HttpResponse("ok")
        
    except Exception as e:
        print(e)
        return HttpResponse(e)

            # else:
            #     msg     = 'NO business Account found '
            #     messages.success(request, msg)
            #     return redirect("/")

    return HttpResponse("no accounts")

def get_sentiment(message):
    import fasttext
    from django.db.models import Q
    model = fasttext.load_model("phonebooth.bin")
    sentimentData = model.predict(str(" ".join(message.split())), k=1)
    if sentimentData[0][0] == "__label__0":
        sentiment = "negative"
    elif sentimentData[0][0] == "__label__2":
        sentiment = "neutral"
    elif sentimentData[0][0] == "__label__4":
        sentiment = "positive"
    else:
        sentiment = "neutral"
    return sentiment

def get_nationality(name):
        import requests
        payload = {}
        headers = {}
    
        name = name.split(" ")

   
        if len(name) > 1:
            first_name = name[0]
            last_name = name[-1]
        else:
            first_name = name[0]
            last_name = ''

        if last_name != "":
            forebears_url = 'https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+first_name+'&sn='+last_name+'&sanitise=1'
        else:
            forebears_url = 'https://ono.4b.rs/v1/nat?key=' + settings.FOREBEARS_KEY + '&fn=' + first_name + '&sn=""&sanitise=1'
  
        response = requests.request("GET", forebears_url, headers=headers, data=payload)
        responseData = response.json()

        if 'countries' in responseData:
            nationality = responseData['countries'][0]
        else:
            nationality = None
        return nationality

def get_fb_replies(graph_page, fbCommentObj, fbPostManagement):
    fbReplyData = graph_page.get_object("/" + str(fbCommentObj['id']) + "/comments")
    if fbReplyData.get('data'):
        if len(fbReplyData.get('data')) > 0:
            for fbReplyObj in fbReplyData.get("data"):
                if 'from' in fbReplyObj:
                    if (fbReplyObj['from']['id'] == fbPostManagement.fb_page.page_id):
                        print("Don't do anything")
                        fbCommentManagementObj = None
                else:
                    fbCommentManagementObj = fb_comment_management(customer_name=fbPostManagement.customer_name,
                    created_time=parser.parse(fbReplyObj.get("created_time")),message=fbReplyObj.get("message"),fb_comment_id=fbReplyObj.get("id"),fb_post_ref=fbPostManagement)
                    fbCommentManagementObj.save()

                if fbCommentManagementObj:
                    # get sentiment
                    sentiment = get_sentiment(fbCommentManagementObj.message)
                    

                    sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                    fbCommentManagementObj.sentiment = sentiment
                    
                    # get location
                    location_url = "https://graph.facebook.com/v8.0/"+fbPostManagement.fb_page.page_id+"?fields=location&access_token="+fbPostManagement.fb_page.page_access_token

                    get_location_url = requests.get(location_url).json()
                    
                    if 'location' in get_location_url:
                        lat = None
                        lon = None
                        location = None
                        if 'city' in get_location_url['location']:
                            location = get_location_url['location']['city'] +', '+get_location_url['location']['country']
                        if 'latitude' in get_location_url['location']:
                            lat = get_location_url['location']['latitude']
                        if 'longitude' in get_location_url['location']:
                            lon = get_location_url['location']['longitude']
                        fbCommentManagementObj.location = location
                        fbCommentManagementObj.location_lat = lat
                        fbCommentManagementObj.location_lon = lon

                    blob = TextBlob(fbCommentManagementObj.message)
                    l = languages.get(alpha2=blob.detect_language())
                    lang = l.name
                    fbCommentManagementObj.comment_language = lang

                    fbCommentManagementObj.save()

                    # get nationality
                    if 'from' in fbCommentObj:
                        nationality = get_nationality(fbCommentObj['from']['name'])
                        if nationality:
                            fbCommentManagementObj.nationality = nationality['jurisdiction']
                            fbCommentManagementObj.nationality_percent = nationality['percent']
                            fbCommentManagementObj.save()

                    fbReplyData = graph_page.get_object("/" + str(fbCommentManagementObj.fb_comment_id) + "/comments")
                 
                    if fbReplyData['data']:
                        
                        print(fbReplyData['data'])
                        fbReplyData['data'][0]['from']['id'] == fbCommentManagementObj.fb_post_ref.fb_page.page_id
                        fbCommentManagementObj.is_replied = True
                        fbCommentManagementObj.save()


def get_facebook_comment(request):
    try:
    # user = request.user    
        fb_comment_management.objects.all().delete()
        try:
            customers = customer_management.objects.filter(user__is_active=True).values_list('user_id', flat=True)
        except Exception as e:
            print("--------------customer-e------------------>")
            print(e)
            customers = None

        social_account = UserSocialAuth.objects.filter(user_id__in=customers, provider = "facebook")
        
        for account in social_account:
            try:
                customer = customer_management.objects.get(user_id=account.user.id)
            except:
                customer = None
            graph = facebook.GraphAPI(access_token=account.extra_data['access_token'])  
            

            # feed = graph.get_object(id=fbData['data'][0]['id'])
            # print(feed)

            # to get page data
            pages_data = graph.get_object(account.uid+"/accounts")
        
            # get page access token
            
            # fb_is_page_management.objects.all().delete()

            for item in pages_data['data']:

                fb_page_exists = fb_is_page_management.objects.filter(customer_name=customer, fb_account=account, page_id=item['id'])
            
                if not fb_page_exists:
                    is_page_removed = removed_fb_page_details.objects.filter(page_id=item['id'], fb_account=account)
                    
                    if not is_page_removed: 
                        fb_page_management = fb_is_page_management.objects.create(customer_name=customer,
                        user_access_token=account.extra_data['access_token'], page_access_token=item['access_token'], page_name=item['name'], page_id=item['id'], fb_account=account)
                        fb_page_management.save()
                    else:
                        pass
                else:
                    fb_page_management = fb_is_page_management.objects.get(customer_name=customer, fb_account=account, page_id=item['id'])
                    
                page_token = item['access_token']
                graph_page = facebook.GraphAPI(access_token=page_token)
                # try:
                fbData = graph_page.get_object("/"+item['id']+"/posts/?limit=25")
                for data in fbData['data']:
                    # get posted picture 
                    pic = graph_page.get_object(data['id'], fields = "full_picture")
                    try:
                        is_post_exists = fb_post_management.objects.filter(customer_name=customer,fb_post_id=data['id'])
                        if not is_post_exists:
                            fbPostManagement = fb_post_management(customer_name=customer,
                                        created_time=parser.parse(
                                        data['created_time']),
                                        message=data['message'],
                                        fb_post_id=data['id'],
                                        fb_account=account,
                                        fb_page=fb_page_management)
                            fbPostManagement.save()
                        
                            if 'full_picture' in pic:
                                full_picture = pic['full_picture']
                                pic_dict = '{"full_picture" : '+ full_picture +'}'
                                fbPostManagement.raw_response = pic_dict
                                fbPostManagement.save()

                        else:
                            fbPostManagement = fb_post_management.objects.get(customer_name=customer,fb_post_id=data['id'])

                        
                    except Exception as e:
                        print("000")
                        print(e)


                    fbPostObj = fb_post_management.objects.get(pk=fbPostManagement.id)

                    fbCommentData = graph_page.get_object("/" + str(fbPostManagement.fb_post_id) + "/comments")

                    if fbCommentData.get('data'):
                        if len(fbCommentData.get('data')) > 0:
                            count = 0
                            for fbCommentObj in fbCommentData.get("data"):
                                count += 1
                                get_fb_replies(graph_page, fbCommentObj, fbPostManagement)
                                
                                if fbCommentObj.get("message") is not None:
                                    fbCommentManagementObj = fb_comment_management(customer_name=fbPostManagement.customer_name,
                                                created_time=parser.parse(fbCommentObj.get("created_time")),message=fbCommentObj.get("message"),fb_comment_id=fbCommentObj.get("id"),fb_post_ref=fbPostObj)
                                    fbCommentManagementObj.save()
                                    
                                # get sentiment
                                sentiment = get_sentiment(fbCommentManagementObj.message)

                                sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                                fbCommentManagementObj.sentiment = sentiment
                                
                                # get location
                                location_url = "https://graph.facebook.com/v8.0/"+item['id']+"?fields=location&access_token="+item['access_token']

                                get_location_url = requests.get(location_url).json()
                                
                                if 'location' in get_location_url:
                                    lat = None
                                    lon = None
                                    location = None
                                    if 'city' in get_location_url['location']:
                                        location = get_location_url['location']['city'] +', '+get_location_url['location']['country']
                                    if 'latitude' in get_location_url['location']:
                                        lat = get_location_url['location']['latitude']
                                    if 'longitude' in get_location_url['location']:
                                        lon = get_location_url['location']['longitude']
                                    fbCommentManagementObj.location = location
                                    fbCommentManagementObj.location_lat = lat
                                    fbCommentManagementObj.location_lon = lon

                                try:
                                    blob = TextBlob(fbCommentManagementObj.message)
                                    
                                    l = languages.get(alpha2=blob.detect_language())
                                    lang = l.name
                                    fbCommentManagementObj.comment_language = lang
                                    fbCommentManagementObj.save()
                                except Exception as e:
                                    print("--------lang---------")
                                    print(e)

                    
                                # get nationality
                                if 'from' in fbCommentObj:
                                    nationality = get_nationality(fbCommentObj['from']['name'])
                                    if nationality:
                                        fbCommentManagementObj.nationality = nationality['jurisdiction']
                                        fbCommentManagementObj.nationality_percent = nationality['percent']
                                        fbCommentManagementObj.save()

                                fbReplyData = graph_page.get_object("/" + str(fbCommentManagementObj.fb_comment_id) + "/comments")
                                if fbReplyData['data']:
                                    if 'from' in fbReplyData['data'][0]:
                                        fbReplyData['data'][0]['from']['id'] == fbCommentManagementObj.fb_post_ref.fb_page.page_id
                                        fbCommentManagementObj.is_replied = True
                                        fbCommentManagementObj.save()
                            
            
            # except Exception as e:
            #     print("-----------------except-------------->")
            #     print(e)
          
    except Exception as e:
        print("-----------------except-------------->")
        print(e)

    return HttpResponse("ok")


def changeStatus(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.is_new = False
        user.save()
    except Exception as e:
        print(e)
    
    return JsonResponse({"success": True})

from PIL import Image
import io
import base64
def download(request):
    image = request.POST.get('data')
    logo = "iVBORw0KGgoAAAANSUhEUgAAAGwAAAAoCAYAAAAbrx+3AAACNElEQVR4nO2av0rDQBjA70kCxU1CQAepdGgXVweHPkDnvkOXPIKjo0MRRxdBiBD8by26BByciiAdiqgoIfo5XXtJLndJ2lxz6feDo9e7S7/78uMuR1sCiFaQZU8AyQYK0wwUphkoTDNQmGagMM1AYZqxEsIcw4oVXVEijBASKtG+IuHJmkdas9lUnkMolpIgEWFsgkUn++E9o7DMQSKCVApjYUWhMFEQJqFowkUne2ZuTesoLG0QibCkrVK0hSY9D3ntFJ6wer0ufL6K5iWbaxGUQljWOiuNFyeLMFEcwzCk8xd9RhGU6hmWtt7r9WLtjuMsXBivvjLC0hzrUZgc5StM1IfC5FROWNZDBwrjBVG8wlgujw9nY1BYyiAl2xIH/SMUJgxSMmG0nic+CluQsCAIuMIcwwLXbEzrjmGB//WZW1i320VhSXXeISJJWPQaiuzbelGcpEMMIQRs25bmUARKhHmel6ovOo53szzPg/F4zB3v+35sPJUz6h+EZP36P8I4AAC1Wi1RANsuymHRKBFWJl72bfmgErNywnSnEsKW+ZO/6r8cVEIYhd68t5PTWJtjWPA+eIzdYN5BhH39CwK4ae2G2qJ1+t5d34bJ9X2hOVZSmExI0nV5+9gybHfmT0RAZYVNru4AAMA1G9Mbfr62Kbwubx8trtlAYWn4Hr0CQPL2JlphFxut2Zb58BTrp323O3uh9mG7gysMkYPCNAOFaQYK0wwUphkoTDNQmGagMM34ByNqGp78LOHYAAAAAElFTkSuQmCC"

    img = image

    base64_images = [logo, img]
    image_files = []

    for base64_string in base64_images:
        buffer = io.BytesIO(base64.b64decode(base64_string))
        
        image_file = Image.open(buffer)
        image_files.append(image_file)


    combined_image = image_files[0].save(
        'output.tiff', 
        save_all=True, 
        append_images=image_files[1:]
        )   
    print(combined_image)       

    return JsonResponse({"success": True})


# import cv2
# import numpy as np

# image1 = cv2.imread("/media/ff.png")[:,:,:3]
# image2 = cv2.imread("/media/ee.png")[:,:,:3]

# class Montage(object):
#     def __init__(self,initial_image):
#         self.montage = initial_image
#         self.x,self.y = self.montage.shape[:2]

#     def append(self,image):
#         image = image[:,:,:3]
#         x,y = image.shape[0:2]
#         new_image = cv2.resize(image,(int(y*float(self.x)/x),self.x))
#         self.montage = np.hstack((self.montage,new_image))
#         return JsonResponse({"success": True})
#     def show(self):
#         cv2.imshow('montage',self.montage)
#         cv2.waitKey()
#         cv2.destroyAllWindows()

def dashboardReports(request):
    context = {}
    twCommentanswered = 0
    twCommentPositive = 0
    twCommentNegative = 0
    fbComment = 0
    instaComment = 0
    user = request.user
    try:
        customerObj = customer_management.objects.get(user=request.user)
        social_accounts = UserSocialAuth.objects.filter(user=request.user)
        twPostObj = twitter_post_management.objects.filter(customer_name=customerObj)
        customerPersonaObj = customer_persona.objects.filter(user=request.user).all().order_by('-id')
        reportTypeObj = ReportTypeMaster.objects.all()

        fbCommentObj = fb_comment_management.objects.filter(customer_name=customerObj, is_replied=False)
        fbCommentunanswered = fbCommentObj.count()

        # for postObj in twPostObj:
        twCommentObj = twitter_comment_management.objects.filter(customer_name=customerObj, is_replied=False)    
        twCommentunanswered = twCommentObj.count()

        twCommentObjpositive = twitter_comment_management.objects.filter(customer_name=customerObj, sentiment=1)
        twCommentPositive = twCommentObjpositive.count()

        twCommentObjnegative = twitter_comment_management.objects.filter(customer_name=customerObj, sentiment=2)
        twCommentNegative = twCommentObjnegative.count()

        instaComment = ig_comment_management.objects.filter(customer_name=customerObj, is_replied=False)
        instaCommentunanswered = instaComment.count()
    

        context = {
            'fbcomment': fbCommentunanswered,
            'twComment': twCommentunanswered,
            'twCommentpositive': twCommentPositive,
            'twCommentnegative': twCommentNegative,
            # 'fbComment': fbComment,
            'instaComment' : instaCommentunanswered,
            "social_accounts": social_accounts,
            'customerPersonaObj': customerPersonaObj,
            'reportTypeObj':reportTypeObj,
            'customer_id': customerObj.id
        }
    except:
        print("000")

    print(context)
    return render(request, "customer/report.html", context)
    # return HttpResponse("ok")
    # return render(request, "customer/report.html", {})


def getCountryName(request):
    responseList = []
    if 'q' in request.GET:
        if request.GET["q"] and request.GET["q"] != "":
            countries = tweet_place_info.objects.filter(country__icontains=request.GET["q"]).distinct("country").values_list('id', 'country')
    else:
        countries = tweet_place_info.objects.all().distinct("country").values_list('id', 'country')

    # sentiment = sentimentMaster.objects.all().values_list('id','sentiment')
    for key, val in countries:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)


def getCityName(request):
    responseList = []
    if 'q' in request.GET:
        if request.GET["q"] and request.GET["q"] != "":
            cities = usa_cities_master.objects.filter(city_name__icontains=request.GET["q"]).distinct("city_name").values_list('id', 'city_name')
    else:
        cities = usa_cities_master.objects.all().values_list('id', 'city_name')

    # sentiment = sentimentMaster.objects.all().values_list('id','sentiment')
    for key, val in cities:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)


def getHashtags(request):
    responseList = []
    if 'q' in request.GET:
        if request.GET["q"] and request.GET["q"] != "":
            hashtags = hashtag_collections.objects.filter(hashtag__icontains=request.GET["q"]).distinct("hashtag").values_list('id', 'hashtag')
    else:
        hashtags = hashtag_collections.objects.all().values_list('id', 'hashtag')

    # sentiment = sentimentMaster.objects.all().values_list('id','sentiment')
    for key, val in hashtags:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)


def getNationality(request):
    responseList = []
    if 'q' in request.GET:
        if request.GET["q"] and request.GET["q"] != "":
            nationality = nationality_prediction.objects.filter(jurisdiction__icontains=request.GET["q"]).distinct("jurisdiction").values_list('id', 'jurisdiction')
    else:
        nationality = nationality_prediction.objects.all().values_list('id', 'jurisdiction')

    # sentiment = sentimentMaster.objects.all().values_list('id','sentiment')
    for key, val in nationality:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)
    
@login_required
def freeListening(request):
    responseList = []
    hashtag_list = []
    cityList = []
    countryList = []
    cultureList = []
    dataList = []
    first_report_empty = False
    secone_report_empty = False
    third_report_empty = False
    forth_report_empty = False
    no_data = True

    hashtags = request.POST.getlist("hashtag")
    cultures = request.POST.getlist("culture")
    countries = request.POST.getlist("countries")
    cities = request.POST.getlist("cities")

    try:

        free_listening_filter = FreeListeningFIlter.objects.filter(user=request.user)
        if free_listening_filter:
            free_listening_filter = FreeListeningFIlter.objects.filter(user=request.user).latest('id')
            if (hashtags or cultures or countries or cities):
                free_listening_filter.countries = countries
                free_listening_filter.cities = cities
                free_listening_filter.hashtags = hashtags
                free_listening_filter.cultures = cultures
                free_listening_filter.save()

        else:
            free_listening_filter = FreeListeningFIlter.objects.create(
                countries = countries,
                cultures = cultures,
                cities = cities,
                hashtags = hashtags,
                user = request.user
            )
    
        
        if (free_listening_filter.countries == '[]' and free_listening_filter.cultures == '[]' and free_listening_filter.hashtags == '[]' and free_listening_filter.cities == '[]'):
            no_data = False

        import json
        if free_listening_filter:
            if free_listening_filter.hashtags:
                # hashtags = free_listening_filter.hashtags
                try:
                    hashtags = [i.split('/')[-1] for i in ast.literal_eval(free_listening_filter.hashtags)]
                except:
                    hashtags = free_listening_filter.hashtags

            if free_listening_filter.cities:
                # cities = free_listening_filter.cities
                try:
                    cities = [i.split('/')[-1] for i in ast.literal_eval(free_listening_filter.cities)]
                except:
                    cities = free_listening_filter.cities

            if free_listening_filter.countries:
                # countries = free_listening_filter.countries
                try:
                    countries = [i.split('/')[-1] for i in ast.literal_eval(free_listening_filter.countries)]
                except:
                    countries = free_listening_filter.countries

            if free_listening_filter.cultures:
                # cultures = free_listening_filter.cultures
                try:
                    cultures = [i.split('/')[-1] for i in ast.literal_eval(free_listening_filter.cultures)]
                except:
                    cultures = free_listening_filter.cultures

        # get countries
        if countries:
            countries = tweet_place_info.objects.filter(id__in=countries)
            for country in countries:
                countryList.append(country.country)

        # get culture
        if cultures:
            cultures = nationality_prediction.objects.filter(id__in=cultures)
            for culture in cultures:
                cultureList.append(culture.jurisdiction)

        # get hashtag
        if hashtags:
            getHashtag = hashtag_collections.objects.filter(id__in=hashtags)
            for hashtag in getHashtag:
                hashtag_list.append(hashtag.hashtag)
        
        hashtag_list.sort()
        hashtag_list.insert(0, "Hashtag")
        
        if cities:
            getCity = usa_cities_master.objects.filter(id__in=cities)
            for city in getCity:
                cityList.append(city.city_name)


        # -------------------------------- Report-1 --------------------------------
        # hashtag comments by location
        get_data = tweet_analytics_processed_data.objects.filter(hashtag__id__in=hashtags, city_code__id__in=cities).values('hashtag__hashtag', 'city_code__city_name').annotate(Count('hashtag'))
        
        
        if hashtag_list:
            dataList = [hashtag_list]
            if len(dataList[0]) == 1:
                if dataList[0][0] == "Hashtag":
                    first_report_empty = True
                
        
        newlist = sorted(get_data, key=lambda k: k['hashtag__hashtag']) 

        if newlist:
            for data in newlist:
                for hashtag in hashtag_list:
                    if 'hashtag__hashtag' in data:
                        if hashtag == data['hashtag__hashtag']:
                            if 'city_code__city_name' in data:
                                for city in cityList:
                                    l = []
                                    if city not in l:
                                        l.append(city)
                                    if l not in dataList:
                                        dataList.append(l)

            for i in newlist:
                for a in dataList:
                    if i['city_code__city_name'] == a[0]:
                        if 'hashtag__count' in i:
                            hashtag = i['hashtag__hashtag']
                            a.append(i['hashtag__count'])
            
            
            for d in dataList:
                if len(hashtag_list) != len(d):
                    index_list = []
                    for i in newlist:
                        
                        if i['city_code__city_name'] == d[0]:
                            hashtag = i['hashtag__hashtag']
                            index = hashtag_list.index(hashtag)
                            index_list.append(index)
                    
                    actual_len = len(hashtag_list)
                    if index_list:
                        for idx in range(actual_len):
                            if idx != 0 and idx not in index_list:
                                d.insert(idx, 0)
                            

                if len(d) == 1:
                    actual_len = len(hashtag_list)
                    for idx in range(actual_len):
                        if idx != 0:
                            d.insert(idx, 0)
        
        else:
            for city in cityList:
                l = []
                if city not in l:
                    l.append(city)
                if l not in dataList:
                    dataList.append(l)

            for d in dataList[1:]:
                actual_len = len(hashtag_list)
                for idx in range(actual_len):
                    if idx != 0:
                        d.insert(idx, 0)


        # -------------------------------- Report-2 --------------------------------
        # Location wise culture distribution
        total_count = 0
        loc_dataList = []

        get_location_data = tweet_analytics_processed_data.objects.filter(tweet_user_jurisdiction__in=cultureList, city_code__id__in=cities).values('tweet_user_jurisdiction', 'city_code__city_name').annotate(Count('tweet_user_jurisdiction'))


        get_location_data = sorted(get_location_data, key=lambda k: k['city_code__city_name'])

        cityList.sort()
        cityList.insert(0, "city")

        loc_dataList.append(cityList)

        if get_location_data:
            for data in get_location_data:
                total_count += data['tweet_user_jurisdiction__count']
                for city in cityList:
                    if 'city_code__city_name' in data:
                        if city == data['city_code__city_name']:
                            for culture in cultureList:
                                l = []
                                if culture not in l and culture not in loc_dataList:
                                        if culture not in l:
                                            l.append(culture)
                                        if l not in loc_dataList:
                                            loc_dataList.append(l)


            for loc in get_location_data:
                for a in loc_dataList:
                    if loc['tweet_user_jurisdiction'] == a[0]:
                        if 'tweet_user_jurisdiction__count' in loc:
                            city = loc['city_code__city_name']
                            loc_index = cityList.index(city)       
                            # percentage = round(loc['tweet_user_jurisdiction__count']/ total_count * 100, 2) 
                            percentage = loc['tweet_user_jurisdiction__count']
                            a.append(percentage)

            
            for d in loc_dataList:
                if len(cityList) != len(d):
                    index_list = []
                    for i in get_location_data:
                        if i['tweet_user_jurisdiction'] == d[0]:
                            city = i['city_code__city_name']
                            index = cityList.index(city)
                            index_list.append(index)
                    
                    actual_len = len(cityList)
                    if index_list:
                        for idx in range(actual_len):
                            if idx != 0 and idx not in index_list:
                                d.insert(idx, 0)
                            

                if len(d) == 1:
                    actual_len = len(cityList)
                    for idx in range(actual_len):
                        if idx != 0:
                            d.insert(idx, 0)

        else:
            for culture in cultureList:
                l = []
                if culture not in l and culture not in loc_dataList:
                    if culture not in l:
                        l.append(culture)
                    if l not in loc_dataList:
                        loc_dataList.append(l)

            for d in loc_dataList[1:]:
                actual_len = len(cityList)
                for idx in range(actual_len):
                    if idx != 0:
                        d.insert(idx, 0)

        
        if len(loc_dataList) == 1:
            secone_report_empty = True

        
        # -------------------------------- Report-3 --------------------------------
        # Location Wise Sentiment Comments For Selected Hashtag
        sentiment_dataList = []
        sentiment_list = ['Sentiment','Negative', "Neutral", "Positive"]

        sentiment_dataList.append(sentiment_list)

        sentiment_comment_data = tweet_analytics_processed_data.objects.filter(city_code__id__in=cities, hashtag__id__in=hashtags).values("tweet_sentiment",  'city_code__city_name').annotate(Count("tweet_sentiment"))

        sentiment_comment_data = sorted(sentiment_comment_data, key=lambda k: k['tweet_sentiment'])


        if sentiment_comment_data:
            for data in sentiment_comment_data:
                print(data)
                for sentiment in sentiment_list:
                    if 'tweet_sentiment' in data:
                        if sentiment.lower() == data['tweet_sentiment']:
                            for city in cityList[1:]:
                                l = []
                                if city not in l and city not in sentiment_dataList:
                                        if city not in l:
                                            l.append(city)
                                        if l not in sentiment_dataList:
                                            sentiment_dataList.append(l)
            

            for i in sentiment_comment_data:
                for a in sentiment_dataList:
                    if i['city_code__city_name'] == a[0]:
                        if 'tweet_sentiment__count' in i:
                            a.append(i['tweet_sentiment__count'])
                    
     
            print("================sentiment_dataList===============>")
            print(sentiment_dataList)

            for d in sentiment_dataList:
                if len(sentiment_list) != len(d):
                    index_list = []
                    for i in sentiment_comment_data:
                        
                        if i['city_code__city_name'] == d[0]:
                            sentiment = i['tweet_sentiment']
                            index = sentiment_list.index(sentiment.title())
                            index_list.append(index)
                    
                    actual_len = len(sentiment_list)
                    if index_list:
                        for idx in range(actual_len):
                            if idx != 0 and idx not in index_list:
                                d.insert(idx, 0)
                            

                if len(d) == 1:
                    actual_len = len(sentiment_list)
                    for idx in range(actual_len):
                        if idx != 0:
                            d.insert(idx, 0)

        else:
            for city in cityList[1:]:
                l = []
                if city not in l and city not in sentiment_dataList:
                    if city not in l:
                        l.append(city)
                    if l not in sentiment_dataList:
                        sentiment_dataList.append(l)
            
            for d in sentiment_dataList[1:]:
                actual_len = len(sentiment_list)
                for idx in range(actual_len):
                    if idx != 0:
                        d.insert(idx, 0)

        if len(sentiment_dataList) == 1:
            third_report_empty = True

        print("--------sentiment------------------------>")
        print(third_report_empty)
        print(sentiment_dataList)

        # -------------------------------- Report-4 --------------------------------
        # Culture Wise Hashtag Usage
        
        culture_dataList = []

        culture_dataList.append(hashtag_list)

        get_culture_data = tweet_analytics_processed_data.objects.filter(tweet_user_jurisdiction__in=cultureList, hashtag__id__in=hashtags).values('tweet_user_jurisdiction', 'hashtag__hashtag').annotate(Count('hashtag'))

        get_culture_data = sorted(get_culture_data, key=lambda k: k['hashtag__hashtag'])

        if get_culture_data:
            for data in get_culture_data:
                for hashtag in hashtag_list:
                    if 'hashtag__hashtag' in data:
                        if hashtag == data['hashtag__hashtag']:
                            if 'tweet_user_jurisdiction' in data:
                                for culture in cultureList:
                                    l = []
                                    if culture not in l and culture not in culture_dataList:
                                            if culture not in l:
                                                l.append(culture)
                                            if l not in culture_dataList:
                                                culture_dataList.append(l)

            for i in get_culture_data:
                for a in culture_dataList:
                    if i['tweet_user_jurisdiction'] == a[0]:
                        if 'hashtag__count' in i:
                            hashtag = i['hashtag__hashtag']
                            a.append(i['hashtag__count'])


            for d in culture_dataList:
                if len(hashtag_list) != len(d):
                    index_list = []
                    for i in get_culture_data:
                        
                        if i['tweet_user_jurisdiction'] == d[0]:
                            hashtag = i['hashtag__hashtag']
                            index = hashtag_list.index(hashtag)
                            index_list.append(index)
                    
                    actual_len = len(hashtag_list)
                    if index_list:
                        for idx in range(actual_len):
                            if idx != 0 and idx not in index_list:
                                d.insert(idx, 0)
                            

                if len(d) == 1:
                    actual_len = len(hashtag_list)
                    for idx in range(actual_len):
                        if idx != 0:
                            d.insert(idx, 0)

        else:
            for culture in cultureList:
                l = []
                if culture not in l and culture not in culture_dataList:
                        if culture not in l:
                            l.append(culture)
                        if l not in culture_dataList:
                            culture_dataList.append(l)


            for d in culture_dataList[1:]:
                actual_len = len(hashtag_list)
                for idx in range(actual_len):
                    if idx != 0:
                        d.insert(idx, 0)


        if len(culture_dataList) == 1:
            forth_report_empty = True


        context = {
            "dataList": dataList,
            "first_report_empty": first_report_empty,

            "loc_dataList": loc_dataList,
            "secone_report_empty": secone_report_empty,

            "sentiment_dataList": sentiment_dataList,
            "third_report_empty": third_report_empty,

            "culture_dataList": culture_dataList,
            "forth_report_empty": forth_report_empty,

            "no_data": no_data
        }

        print("=============CONTEXT=====================>")
        print(context)
        
        return render(request, "customer/free_listening/index.html", context)

    except Exception as e:
        print("===============EXCEPTION========================>")
        print(e)
        context = {}
        return render(request, "customer/free_listening/index.html", context)
    

def getFilterData(request):
    user = request.user
    filters = FreeListeningFIlter.objects.filter(user = user)
    for fltr in filters:
        cultures = fltr.cultures
        cities = fltr.cities
        hashtags = fltr.hashtags
        countries = fltr.countries

    print("---------cultures---------------->")
    # x = ast.literal_eval(cities)
    
    
    # x = [n.strip() for n in x]
    
    cultureList = []
    cityList = []
    hashtagList = []
    countryList = []

    if cultures:
        cultures = [i.split('/')[-1] for i in ast.literal_eval(cultures)]
        cultures = nationality_prediction.objects.filter(id__in=cultures)
        for val in cultures:
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.jurisdiction
            cultureList.append(responseDict)

    if cities:
        cities = [i.split('/')[-1] for i in ast.literal_eval(cities)]
        cities = usa_cities_master.objects.filter(id__in=cities)
        for val in cities:
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.city_name
            cityList.append(responseDict)

    if hashtags:
        hashtags = [i.split('/')[-1] for i in ast.literal_eval(hashtags)]
        hashtags = hashtag_collections.objects.filter(id__in=hashtags)
        for val in hashtags:
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.hashtag
            hashtagList.append(responseDict)
    
    if countries:
        countries = [i.split('/')[-1] for i in ast.literal_eval(countries)]
        countries = tweet_place_info.objects.filter(id__in=countries)
        for val in countries:
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.country
            countryList.append(responseDict)
        
   

    data = {
        "cities" : cityList,
        "countries": countryList,
        "hashtags": hashtagList,
        "cultures": cultureList
    }

    return JsonResponse(data)