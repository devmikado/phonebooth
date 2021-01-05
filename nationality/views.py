from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse, Http404
import sys, os
from phonebooth import settings
from .models import *
import json
from datetime import datetime
import re
import twitter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib
from django.db.models import Count
from phonebooth.decorators import is_superuser

import io
import base64
from xml.sax import saxutils
from .forms import *
from math import log, floor

class TwitterAPIDataConnection(TemplateView):
    def twitter_data_collection(request):
        # To Do : hashtag collection entries loop
        hashtag_collections.objects.filter(is_processed=True, is_locked=True).update(is_processed=False, is_locked=False)
        hashtag_collections.objects.filter(is_locked=True, is_processed=False).update(is_processed=False, is_locked=False)
        unProcessTags = hashtag_collections.objects.filter(is_processed=False,is_locked=False).all()
        allUsaCities = usa_cities_master.objects.all()
        from datetime import datetime
        from time import sleep
        maxtweetsPerQry = 150  # this is the max the API permits
        tweetPerQuery = 0
        for usaCity in allUsaCities:
            for getTags in unProcessTags:
                if tweetPerQuery < maxtweetsPerQry:
                    TwitterAPIDataConnection.twitterRestApiEffective(request,search_object=getTags, city_object=usaCity, state_object=usaCity.usa_state)
                    tweetPerQuery = tweetPerQuery + 1
                    print("\n incremented count for tweetPerQuery "+str(tweetPerQuery))
                else:
                    print("I am going to sleep for next 15 mins........!!!")
                    sleep(900)  # Wait for 15 minutes
                    tweetPerQuery = 0
                    continue

        return HttpResponse("Data has been collected Successfully...........")

    
    def twitterRestApiEffective(self,search_object, city_object, state_object):
        api = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                          consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                          access_token_key="454475197-8wgIsjso71gfrkqoKAEZdspXZCm3nj4sOvjvafeD",
                          access_token_secret="kFS9MPMWuPfoZKvneQ15wp7flIOVvB1fZsVkPzJFbpjUz",
                          sleep_on_rate_limit=True)

        results = api.GetSearch(raw_query="q=" + str(search_object.hashtag) + "&count=10000&geocode=" + str(city_object.latitude) + "," + str(city_object.longitude) + ",1000km")
        resultAsDict = {}
        key = 0
        for rs in results:
            resultAsDict[key] = rs.AsDict()
            key = key + 1
            searchAPI = data_collection_logging(
                searched_text=str(search_object.hashtag),
                request='q="' + str(search_object.hashtag) + '"&count=10&geocode=' + str(city_object.latitude) + ',' + str(city_object.longitude) + ',1000km',
                response=resultAsDict,
                hashtag=search_object,
                state_code=state_object,
                city_code=city_object,
            )
            searchAPI.save()

        return True

    def human_format(number):
        magnitude = 0
        while abs(number) >= 1000:
            magnitude += 1
            number /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (number, ['','K', 'M', 'G', 'T', 'P'][magnitude])

    @login_required
    @is_superuser
    def phonebooth_dashboard(request):
        chipForm = createChipForm
        # # TwitterAPIDataConnection.human_format()
        LOCATIONOPTIONS = usa_cities_master.objects.all().values_list('city_name', 'city_name')
        NATIONALITYOPTIONS = nationality_prediction.objects.distinct('jurisdiction').all().values_list('jurisdiction', 'jurisdiction')
        HASHTAGOPTIONS = hashtag_collections.objects.all().values_list('hashtag', 'hashtag')
        # chipTileObj = chiptiles.objects.all().order_by('-id')

        context = {}
        context['LOCATIONOPTIONS'] = LOCATIONOPTIONS
        context['NATIONALITYOPTIONS'] = NATIONALITYOPTIONS
        context['HASHTAGOPTIONS'] = HASHTAGOPTIONS
        # context['chipTileObj'] = chipTileObj
        context['chipForm'] = chipForm
        # context['total_tweets'] = TwitterAPIDataConnection.human_format(tweet_basic_info.objects.filter().count())
        # context['collected_hashtags'] = TwitterAPIDataConnection.human_format(hashtag_collections.objects.filter().count())
        # context['collected_places'] = TwitterAPIDataConnection.human_format(tweet_place_info.objects.filter().distinct('place_name','place_id','tweet_basic_info_ref').count())
        # context['collected_users'] = TwitterAPIDataConnection.human_format(nationality_prediction.objects.filter().count())

        return render(request, 'nationality/index.html', context)


    @login_required
    @is_superuser
    def getLocationsList(request):
        if request.GET["q"] and request.GET["q"] != "":
            LOCATIONOPTIONS = usa_cities_master.objects.distinct('city_name').filter(city_name__icontains=request.GET["q"]).values_list('city_name', 'city_name').order_by('city_name')
        else:
            LOCATIONOPTIONS = usa_cities_master.objects.distinct('city_name').all().values_list('city_name','city_name').order_by('city_name')
        responseList = []
        for key, val in LOCATIONOPTIONS:
            responseDict = {}
            responseDict["id"] = key
            responseDict["text"] = val
            responseList.append(responseDict)
        return JsonResponse(responseList, safe=False)

    @login_required
    @is_superuser
    def getHashtagsList(request):
        if request.GET["q"] and request.GET["q"] != "":
            HASHTAGOPTIONS = hashtag_collections.objects.distinct('hashtag').filter(hashtag__icontains=request.GET["q"]).values_list('hashtag', 'hashtag').order_by('hashtag')
        else:
            HASHTAGOPTIONS = hashtag_collections.objects.distinct('hashtag').all().values_list('hashtag','hashtag').order_by('hashtag')
        responseList = []
        for key, val in HASHTAGOPTIONS:
            responseDict = {}
            responseDict["id"] = key
            responseDict["text"] = val
            responseList.append(responseDict)
        return JsonResponse(responseList, safe=False)

    @login_required
    @is_superuser
    def getNationalitiesList(request):
        if request.GET["q"] and request.GET["q"] != "":
            NATIONALITYOPTIONS = nationality_prediction.objects.distinct('jurisdiction').filter(jurisdiction__icontains=request.GET["q"]).values_list('jurisdiction','jurisdiction')
        else:
            NATIONALITYOPTIONS = nationality_prediction.objects.distinct('jurisdiction').all().values_list('jurisdiction', 'jurisdiction')
        responseList = []
        for key, val in NATIONALITYOPTIONS:
            responseDict = {}
            responseDict["id"] = key
            responseDict["text"] = val
            responseList.append(responseDict)
        return JsonResponse(responseList, safe=False)


    @login_required
    @is_superuser
    def addnewchip(request):
        if request.method == 'POST':
            responseDict = {}
            print(request.POST)
            form = createChipForm(request.POST)
            # check whether it's valid:
            if not request.POST.get('chip_title'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter title'
                return JsonResponse(responseDict)

            if not request.POST.get('start_date'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter Start Date'
                return JsonResponse(responseDict)

            if not request.POST.get('end_date'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter End Date'
                return JsonResponse(responseDict)

            if not request.POST.getlist('locations') and not request.POST.getlist('hashtags') and not request.POST.getlist('nationalities'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please select atleast locations, hashtags or nationalities'
                return JsonResponse(responseDict)

            if form.is_valid():
                chip_title = form.cleaned_data['chip_title']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                if request.POST.getlist('nationalities'):
                    nationalities = ','.join(request.POST.getlist('nationalities'))
                else:
                    nationalities = ""
                if request.POST.getlist('locations'):
                    locations = ','.join(request.POST.getlist('locations'))
                else:
                    locations = ""

                if request.POST.getlist('hashtags'):
                    hashtags = ','.join(request.POST.getlist('hashtags'))
                else:
                    hashtags = ""

                chipTileModelObj = chiptiles(
                    chip_title = chip_title,
                    start_date = start_date,
                    end_date = end_date,
                    nationalities = nationalities,
                    locations = locations,
                    hashtags = hashtags
                )
                try:
                    chipTileModelObj.save()
                except Exception as e:
                    print(e)
                    # raise exception or error message
                    messages.error(request, 'Error while creating chip !')
                    responseDict['success'] = 0
                    responseDict['message'] = 'Error while creating chip'
                else:
                    messages.success(request, 'Chip has been created successfully !')
                    responseDict['success'] = 1
                    responseDict['message'] = 'Chip has been created successfully'
            else:
                responseDict = {}
                responseDict['success'] = 0
                responseDict['message'] = "form is not valid"
            return JsonResponse(responseDict)



class TwitterDataProcessing(TemplateView):

    def unicode_slugify(value):
        import unicodedata
        from unidecode import unidecode
        returnString = ""

        for character in value:
            try:
                character.encode("ascii")
                returnString += character
            except UnicodeEncodeError:
                returnString = ""
        return returnString


    def process_collected_twits(request):

        data_collection_logging.objects.filter(is_locked=True, is_processed=False).update(is_locked=False, is_processed=False)

        # data_collection_logging.objects.filter(is_locked=True, is_processed=True, pk__in=unProcessedids).update(is_locked=False, is_processed=False)

        # Collect data from twitter_standard_api where locked False and processed False
        getunProcessedids = data_collection_logging.objects.filter(is_locked=True, is_processed=True).values_list("id",flat=True)
        unProcessedids = [x for x in getunProcessedids]
        # if any getunProcessedids in list
        if len(getunProcessedids)>0:
            # Update locked True to all getunProcessedids
            data_collection_logging.objects.filter(is_locked=False, is_processed=False, pk__in=unProcessedids).update(is_locked=True)

            # Collected Locked Rows
            getProcessedData = data_collection_logging.objects.filter(is_locked=True,is_processed=False).all()

            # Iterate locked Rows
            for gData in getProcessedData:
                # convert strint to Dict using eval method
                newDataDict = eval(gData.response)
                for k,v in newDataDict.items():

                    # Save data into tweet_basic_info which contains tweet text, tweet lang
                    basicInfoData = tweet_basic_info(
                        tweet_id=v.get("id"),
                        tweet_text=v.get("text"),
                        tweet_source=v.get("source"),
                        is_tweet_truncated=v.get("truncated",False),
                        tweet_lang=v.get("lang"),
                        tweet_created_datetime=datetime.strptime(v.get("created_at"), '%a %b %d %H:%M:%S %z %Y'),
                        hashtag = gData.hashtag,
                        state_code = gData.state_code,
                        city_code = gData.city_code,
                        data_collection_log = gData

                    )
                    basicInfoData.save() # Basic data has been saved successfully

                    # Save data into tweet_place_info which contains place of tweet, country. place name etc
                    if "place" in v:
                        placeInfoData = tweet_place_info(
                            tweet_basic_info_ref=basicInfoData,
                            place_id=v.get("place").get("id"),
                            place_type=v.get("place").get("place_type"),
                            place_name=v.get("place").get("name"),
                            place_full_name=v.get("place").get("full_name"),
                            country_code=v.get("place").get("country_code"),
                            country = v.get("place").get("country"),
                            hashtag = gData.hashtag,
                            state_code = gData.state_code,
                            city_code = gData.city_code,
                        )
                        placeInfoData.save() # Placed data has been saved successfully

                    # Save data into tweet_entities_hashtags which contains hashtags which has been used in tweet text
                    if "hashtags" in v:
                        if len(v.get("hashtags")) > 0:
                            tweetEntitiesHashtags = tweet_entities_hashtags(
                                tweet_basic_info_ref = basicInfoData,
                                twit_hashtags = ",".join([x.get("text") for x in v.get("hashtags")]),
                                hashtag = gData.hashtag,
                                state_code = gData.state_code,
                                city_code = gData.city_code,
                            )
                            tweetEntitiesHashtags.save() # tweet hashtags has been saved successfully

                    # Save data into tweet_entities_user_mentions if any user mentioned into tweet
                    if "user_mentions" in v:
                        if len(v.get("user_mentions")) > 0:
                            tweetEntitiesUserMention = tweet_entities_user_mentions(
                                tweet_basic_info_ref = basicInfoData,
                                user_mentions = ",".join([x.get("name") for x in v.get("user_mentions")]),
                                hashtag = gData.hashtag,
                                state_code = gData.state_code,
                                city_code = gData.city_code,
                            )
                            tweetEntitiesUserMention.save() # tweet user mentioned data has been saved successfully.


                    # Save data into tweet_entities_user_urls if any urls has been mentioned into tweet text
                    if "urls" in v:
                        tweetEntitiesUserUrls = tweet_entities_user_urls(
                            tweet_basic_info_ref=basicInfoData,
                            urls=",".join([x.get("url") for x in v.get('urls')]),
                            hashtag = gData.hashtag,
                            state_code = gData.state_code,
                            city_code = gData.city_code,
                        )
                        tweetEntitiesUserUrls.save() # Tweet Entities User URLS data has been saved successfully.

                    # Save data into tweet_metadata for tweet like tweet language code and tweet is recent etc.
                    if "metadata" in v:
                        tweetMetaData = tweet_metadata(
                            tweet_basic_info_ref=basicInfoData,
                            iso_language_code=v.get("metadata").get("iso_language_code"),
                            result_type=v.get("metadata").get("result_type"),
                            hashtag = gData.hashtag,
                            state_code = gData.state_code,
                            city_code = gData.city_code,
                        )
                        tweetMetaData.save() # Tweet MetaData has been saved successfully.

                    # Save data into tweetTwitterAPIConnection_user_data of user who has been made this tweet
                    # This will contain name, screen_name, location, description, lang, geo_enabled etc etc
                    if "user" in v:
                        tweetUserData = tweet_user_data(
                            tweet_basic_info_ref=basicInfoData,
                            tweet_user_id=v.get("user").get("id"),
                            name =re.sub('[^A-Za-z]+', ' ', v.get("user").get("name")),
                            screen_name =v.get("user").get("screen_name"),
                            location =v.get("user").get("location"),
                            description =v.get("user").get("description"),
                            url =v.get("user").get("url"),
                            is_protected =v.get("user").get("protected",False),
                            profile_created_at =datetime.strptime(v.get("user").get("created_at"), '%a %b %d %H:%M:%S %z %Y'),
                            utc_offset =v.get("user").get("utc_offset"),
                            time_zone =v.get("user").get("time_zone"),
                            geo_enabled =v.get("user").get("geo_enabled",False),
                            verified =v.get("user").get("verified",False),
                            lang =v.get("user").get("lang"),
                            hashtag = gData.hashtag,
                            state_code = gData.state_code,
                            city_code = gData.city_code,
                        )

                        if tweetUserData.name.strip() != "":
                            tweetUserData.save() # Tweet User Data has been saved successfully.

                data_collection_logging.objects.filter(pk__exact=gData.id).update(is_processed=True)

        return HttpResponse("Data has been Processed Successfully...........")




    ''' Following method is getting use for ethnicity data preparation '''
    def prepare_nationality_data(request):
        #ethnicity_user_data_preprocess.objects.filter().delete()
        # Collect data from Tweet Basic Info having is_pre_processed = False
        getUnprocessedInfo = tweet_basic_info.objects.filter(is_pre_processed=False).all()
        getUnprocessedids = [x for x in getUnprocessedInfo]

        # Collect distince tweet_user_id which is profile id
        # UserInfo from tweet_user_data having tweet_basic_info_ref id's in getUnprocessedids
        collectUserInfo = tweet_user_data.objects.filter(tweet_basic_info_ref__in=getUnprocessedids).distinct("tweet_user_id").all()

        # Iterate collectUserInfo query Obj
        for userInfo in collectUserInfo:
            user_id = userInfo
            # If user name is mentioned in non-ascii then we are making those in unicode format using def : unicode_slugify
            tweetProfileName = TwitterDataProcessing.unicode_slugify(userInfo.name)
            # name is coming with multiple words so we are splitting those with space and considering first as first name other are last name
            nameData = tweetProfileName.split(" ")
            if(len(nameData)):
                f_name = nameData[0]
                l_name = " ".join(nameData[1:len(nameData)])
            else:
                f_name = None
                l_name = None

            # Most of the cases locations come with blank so we have checked its status
            if userInfo.location is not None:
                loc = TwitterDataProcessing.unicode_slugify(userInfo.location)
            else:
                loc = None

            # Most of the cases Language come with blank so we have checked its status
            if userInfo.lang is not None:
                lan = userInfo.lang
            else:
                lan = None

            forebears_url = 'https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+'Absar'+'&sn='+'khan'+'&sanitise=1'

            # https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+fn+'&sn='+sn+'&sanitise=1

            import requests
            payload = {}
            headers = {}
            response = requests.request("GET", forebears_url, headers=headers, data=payload)
            responseData = response.json()

            # print(responseData)
            # return JsonResponse(responseData)

            # Preparing dataset for ethnicity detection and added into db table ethnicity_user_data_preprocess
            nationalityDataPreprocess = nationality_user_data_preprocess(
                tweet_user_data_ref = user_id,
                first_name=f_name,
                last_name=l_name,
                location=loc,
                lang=lan,
                hashtag=userInfo.hashtag,
                state_code=userInfo.state_code,
                city_code=userInfo.city_code,
            )
            nationalityDataPreprocess.save()

        return HttpResponse("Data has been Prepared...........")

    
    def nationality_prediction_data_process(request):

        dataList = []
        updateLockedid = []
        # collect Unprocessed User's data from ethnicity_user_data_preprocess
        nationality_user_data_preprocess.objects.filter(is_locked=True, is_processed=False).update(is_locked=False)
        collectUnProcessedids = nationality_user_data_preprocess.objects.filter(is_locked=False, is_processed=False).values_list("id", flat=True)
        
        unProcessedids = [x for x in collectUnProcessedids]

        
        if len(unProcessedids) > 0:
            # Locked Unprocessed User's data
            nationality_user_data_preprocess.objects.filter(is_locked=False, is_processed=False, pk__in=unProcessedids).update(is_locked=True)

            # Collect Unprocessed and Locked User's data
            collectUnProcessedData = nationality_user_data_preprocess.objects.filter(is_locked=True, is_processed=False)

            for cuData in collectUnProcessedData:
                if cuData.first_name != "":
                    fn = cuData.first_name
                else:
                    fn = ""

                if cuData.last_name != "":
                    sn = cuData.last_name
                else:
                    sn = ""

                isRecord_exist = nationality_prediction.objects.filter(first_name__exact=fn, last_name__exact=sn).count()
                if isRecord_exist > 0:
                    nationality_user_data_preprocess.objects.filter(pk__exact=cuData.id, is_locked=True, is_processed=False).update(is_locked=True)
                    ''' Check this entries do we have already in dataset '''
                    isRecord_exist = nationality_prediction.objects.filter(first_name__exact=fn, last_name__exact=sn).count()
                    
                else:
                    if sn != "":
                        forebears_url = 'https://ono.4b.rs/v1/nat?key='+settings.FOREBEARS_KEY+'&fn='+fn+'&sn='+sn+'&sanitise=1'
                    else:
                        forebears_url = 'https://ono.4b.rs/v1/nat?key=' + settings.FOREBEARS_KEY + '&fn=' + fn + '&sn=""&sanitise=1'
                    try:
                        import requests
                        payload = {}
                        headers = {}
                        response = requests.request("GET", forebears_url, headers=headers, data=payload)
                        responseData = response.json()
                        
                        # forebears log given entry
                        forebearsLogging = forebears_logging(
                            first_name=fn,
                            last_name=sn,
                            request_text=forebears_url,
                            response_text=response.json(),
                            hashtag=cuData.hashtag,
                            state_code=cuData.state_code,
                            city_code=cuData.city_code,
                            tweet_user_data_ref = cuData.tweet_user_data_ref
                        )
                        forebearsLogging.save()
                    
                        sanitisedFirstname = responseData.get('sanitisedForename')
                        sanitisedLastname = responseData.get('sanitisedSurname')
                        nationality_list = responseData.get('countries')
                        if nationality_list is not None:
                            for nlist in nationality_list[0:1]:
                                jurisdiction = nlist.get('jurisdiction')
                                percent = nlist.get('percent')
                        else:
                            jurisdiction = ""
                            percent = ""
                        # nationality prediction data
                        nationalityPrediction = nationality_prediction(
                            first_name=fn,
                            last_name=sn,
                            jurisdiction=jurisdiction,
                            percent=percent,
                            sanitisedForename = sanitisedFirstname,
                            sanitisedSurname = sanitisedLastname,
                            state_code=cuData.state_code,
                            city_code=cuData.city_code,
                            tweet_user_data_ref = cuData.tweet_user_data_ref
                        )
                        if nationalityPrediction.percent != "":
                            nationalityPrediction.save()
                    except Exception as e:
                        print(e)
        # update processed ethnicity_user_data_preprocess
        nationality_user_data_preprocess.objects.filter(is_locked=True, pk__in=updateLockedid).update(is_processed=True)

        return HttpResponse("nationality has been predicted")


def get_sentiment(message):
        import fasttext
        from django.db.models import Q
        model = fasttext.load_model("phonebooth.bin")
        sentimentData = model.predict(str(" ".join(message.split())), k=3)
        if sentimentData[0][0] == "__label__0":
            sentiment = "negative"
        elif sentimentData[0][0] == "__label__2":
            sentiment = "neutral"
        elif sentimentData[0][0] == "__label__4":
            sentiment = "positive"
        else:
            sentiment = "neutral"

        return sentiment


def get_country(tweet_info_obj):
    print(tweet_info_obj.id)
    place_info = tweet_place_info.objects.filter(tweet_basic_info_ref=tweet_info_obj)

    if place_info:
        place = place_info.get(tweet_basic_info_ref=tweet_info_obj)
        
        return place
    else:
        return None



class TweeterDataPreprocess(TemplateView):
    def prepareTweeterDataPreprocess(request):
        tweet_analytics_processed_data.objects.all().delete()
        tweetUserData = tweet_user_data.objects.all()
        for userObj in tweetUserData:

            tweet_user_id = userObj.tweet_user_id
            tweet_username = userObj.name
            fullName = userObj.name.split(' ')
            if len(fullName) > 1:
                first_name = fullName[0]
                last_name = fullName[1]
            else:
                first_name = fullName[0]
                last_name = ""
            tweet_user_location = userObj.location
            tweet_user_description = userObj.description
            tweet_user_profile_created_at = userObj.profile_created_at
            try:
                userNatioanlityData = nationality_prediction.objects.get(first_name__icontains=first_name, last_name__icontains=last_name)
                tweet_user_first_name = userNatioanlityData.first_name
                tweet_user_last_name = userNatioanlityData.last_name
                tweet_user_nationality_predicted = True
                tweet_user_jurisdiction = userNatioanlityData.jurisdiction
                tweet_user_percent = userNatioanlityData.percent
            except Exception as e:
                tweet_user_first_name = None
                tweet_user_last_name = None
                tweet_user_nationality_predicted = False
                tweet_user_jurisdiction = None
                tweet_user_percent = 0.00
                print(e.args)
            tweet_id = userObj.tweet_basic_info_ref.tweet_id
            tweet_text = userObj.tweet_basic_info_ref.tweet_text
            tweet_lang = userObj.tweet_basic_info_ref.tweet_lang
            tweet_created_datetime = userObj.tweet_basic_info_ref.tweet_created_datetime
            state_code = userObj.state_code
            city_code = userObj.city_code
            hashtag = userObj.hashtag

            # get sentiment
            sentiment = get_sentiment(tweet_text)
            print("-----------sentiment------------->")
            print(sentiment)

            # get country
            country_obj = get_country(userObj.tweet_basic_info_ref)
            print("------------country_obj---------------------->")
            print(country_obj)


            tweet_analytics_processed_data_Obj = tweet_analytics_processed_data(
                tweet_user_id=tweet_user_id,
                tweet_username=tweet_username,
                tweet_user_location=tweet_user_location,
                tweet_user_description=tweet_user_description,
                tweet_user_profile_created_at=tweet_user_profile_created_at,
                tweet_user_first_name=tweet_user_first_name,
                tweet_user_last_name=tweet_user_last_name,
                tweet_user_nationality_predicted=tweet_user_nationality_predicted,
                tweet_user_jurisdiction=tweet_user_jurisdiction,
                tweet_user_percent=tweet_user_percent,
                tweet_id=tweet_id,
                tweet_text=tweet_text,
                tweet_lang=tweet_lang,
                tweet_created_datetime=tweet_created_datetime,
                state_code=state_code,
                city_code=city_code,
                hashtag=hashtag,
                tweet_sentiment = sentiment
            )
            tweet_analytics_processed_data_Obj.save()
        return HttpResponse("All rows has been executed ...................!!!")