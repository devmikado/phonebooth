from django import template
from django.db.models import Q
from ..models import *

register = template.Library()

@register.simple_tag(name="get_tweet_collection_count")
def get_tweet_collection_count(start_date, end_date, locations="", nationalities="", hashtags=""):
    # Showing category to menu when is visible in admin side
    dataCollectionObj = tweet_analytics_processed_data.objects.filter(tweet_created_datetime__range=[start_date, end_date], tweet_user_nationality_predicted=True)
    if nationalities != "":
        nationalityDataList = nationalities.split(',')
        nationalityData = [x.strip(' ') for x in nationalityDataList]
        dataCollectionObj = dataCollectionObj.filter(tweet_user_jurisdiction__in=nationalityData)

    if locations != "":
        locationDataList = locations.split(',')
        locationData = [x.strip(' ') for x in locationDataList]
        dataCollectionObj = dataCollectionObj.filter(city_code__in=locationData)

    if hashtags != "":
        hashtagsDataList = hashtags.split(',')
        hashtagsData = [x.strip(' ') for x in hashtagsDataList]
        dataCollectionObj = dataCollectionObj.filter(hashtag__in=hashtagsData)

    resultData = {"dataCollectionObjCount": dataCollectionObj.count()}
    print("000000000000000000000000000000000000000000")
    print(resultData)
    return resultData


@register.simple_tag(name="get_hashtag_collection_count")
def get_hashtag_collection_count(start_date, end_date, hashtags="", locations=""):

    hashtagCollectionObj = tweet_entities_hashtags.objects.filter(created_on__range=[start_date, end_date])
    if hashtags != "":
        collected_hashtag = hashtags.split(",")
        hashtagCollectionObj = hashtagCollectionObj.filter(hashtag__in=collected_hashtag)
    if locations != "":
        locations = locations.split(",")
        hashtagCollectionObj = hashtagCollectionObj.filter(city_code__in=locations)

    hashString = ""
    for hash in hashtagCollectionObj:
        hashString += ","+hash.hashtags

    hashSet = set()
    if len(hashString) > 0:
        hashData = hashString.split(",")
        for hash in hashData:
            hashSet.add(hash)

    collected_hashtags = list(hashSet)
    collected_hashtagsCount = len(list(hashSet))
    resultDict = {"collected_hashtags":collected_hashtags, "collected_hashtagsCount":collected_hashtagsCount}
    return resultDict

@register.simple_tag(name="get_nationality_collection_count")
def get_nationality_collection_count(start_date, end_date, locations="", nationalities="", hashtags=""):
    # Showing category to menu when is visible in admin side
    dataCollectionObj = tweet_analytics_processed_data.objects.distinct('tweet_user_id').filter(
        tweet_created_datetime__range=[start_date, end_date], tweet_user_nationality_predicted=True)
    if nationalities != "":
        nationalityDataList = nationalities.split(',')
        nationalityData = [x.strip(' ') for x in nationalityDataList]
        dataCollectionObj = dataCollectionObj.filter(tweet_user_jurisdiction__in=nationalityData)

    if locations != "":
        locationDataList = locations.split(',')
        locationData = [x.strip(' ') for x in locationDataList]
        dataCollectionObj = dataCollectionObj.filter(city_code__in=locationData)

    if hashtags != "":
        hashtagsDataList = hashtags.split(',')
        hashtagsData = [x.strip(' ') for x in hashtagsDataList]
        dataCollectionObj = dataCollectionObj.filter(hashtag__in=hashtagsData)

    return dataCollectionObj.count()


@register.simple_tag(name="selected_counts")
def selected_counts(selected_string):

    if selected_string != "":
        selected_list = selected_string.split(',')
        return len(selected_list)
    else:
        return "N/A"

@register.simple_tag(name="selected_chipwise_fb_comments")
def selected_chipwise_fb_comments(chip_id):
    fbComment = 0
    chipObj = customer_chiptiles.objects.get(pk__exact=chip_id)
    fbPostObj = fb_post_management.objects.filter(customer_chip_ref=chipObj)
    for postObj in fbPostObj:
        fbCommentObj = fb_comment_management.objects.filter(fb_post_ref=postObj)
        fbComment = fbComment+fbCommentObj.count()
    return fbComment

@register.simple_tag(name="selected_chipwise_tw_comments")
def selected_chipwise_tw_comments(chip_id):
    twComment = 0
    chipObj = customer_chiptiles.objects.get(pk__exact=chip_id)
    twPostObj = twitter_post_management.objects.filter(customer_chip_ref=chipObj)
    for postObj in twPostObj:
        twCommentObj = twitter_comment_management.objects.filter(twitter_post_ref=postObj)
        twComment = twComment+twCommentObj.count()
    return twComment

@register.simple_tag(name="selected_chipwise_ig_comments")
def selected_chipwise_ig_comments(chip_id):
    igComment = 0
    chipObj = customer_chiptiles.objects.get(pk__exact=chip_id)
    igPostObj = ig_post_management.objects.filter(customer_chip_ref=chipObj)
    for postObj in igPostObj:
        igCommentObj = ig_comment_management.objects.filter(ig_post_ref=postObj)
        igComment = igComment+igCommentObj.count()
    return igComment