# Celery Imports
from celery.schedules import crontab
from celery.decorators import periodic_task, task
from celery.utils.log import get_task_logger
from celery import shared_task

from datetime import timedelta

import twitter
from dateutil import parser
from langdetect import detect

from .views import SocialMediaPlatform
from b2b.models import *
from nationality.models import *
from social_django.models import UserSocialAuth
from django.conf import settings

logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(minute='*/30')), name="some_task", ignore_result=True)
def some_task():
    # do something
    print("----------hello======================>")



@periodic_task(
    run_every=(crontab(minute='*/15')),
    name="get_tweets",
    ignore_result=True
)
def get_all_tweets():
    customers = customer_management.objects.filter(user__is_active=True).values_list('user_id', flat=True)
    twitter_credentials = UserSocialAuth.objects.filter(provider='twitter', user_id__in=customers)
    
    # # twitter_credentials = UserSocialAuth.objects.filter(id=37)
    # # twitter_post_management.objects.filter(customer_name=customer).delete()
    twitter_comment_management.objects.all().delete()
    try:
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
            
            try:
                verifyData = api.VerifyCredentials()
                statuses = api.GetUserTimeline(screen_name=verifyData.screen_name)

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
                            twitReplyObj = twitter_post_management.objects.filter(customer_name=customer, tweet_id=status.in_reply_to_status_id)
                            
                            if twitReplyObj:
                                for i in twitReplyObj:
                                    twitter_obj = i



                            if twitter_obj != None:
                                print("-----------in if------------------->")
                                print(customer)
                                print(customer.id)
                                
                                print(twitter_obj.tweet_id)
                                # print(status)
                                try:
                                    twPostManagementObj = twitter_comment_management(customer_name=customer,created_time=parser.parse(status.created_at),message=status.text,tweet_reply_id=status.id,twitter_post_ref=twitter_obj)

                                    twPostManagementObj.save()

                                    print(twPostManagementObj)
                                except Exception as e:
                                    print("--------------ee---------------")
                                    print(e)

                                # get sentiment
                                sentiment = SocialMediaPlatform.get_sentiment(twPostManagementObj)
                            
                                # get nationality
                                nationality = SocialMediaPlatform.get_nationality(api, status)
                            
                                twPostManagementObj.nationality = nationality['jurisdiction']
                                twPostManagementObj.nationality_percent = nationality['percent']

                                # get language of comment
                                lang = detect(status.text)
                                twPostManagementObj.comment_language = lang

                                if status.user.location:
                                    geolocator = Nominatim(user_agent='myapplication')
                                    location = geolocator.geocode(status.user.location)
                                    location_lat = location.raw.lat
                                    location_lon = location.raw.login
                                    location = location.raw.display_name

                                    twPostManagementObj.location = location
                                    twPostManagementObj.location_lat = location_lat
                                    twPostManagementObj.location_lon = location_lon

                                    twPostManagementObj.save()

                            
                                twPostManagementObj.save()
                                
                                try:
                                    sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                                except Exception as e:
                                    print("888888888888888888888888888888888888")
                                    print(e)
                                twPostManagementObj.sentiment = sentiment
                                twPostManagementObj.save()
                                SocialMediaPlatform.get_replies(customer, status)
                            else:
                                pass


            except Exception as e:
                print("-----------except-2----------")
                print(e)



    except Exception as e:
        print("----------final exception------------->")
        print(e)



            

