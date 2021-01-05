from dateutil import parser
import facebook
from b2b.models import *
from social_django.models import UserSocialAuth
from django.apps.registry import apps
from langdetect import detect
from textblob import TextBlob
from iso639 import languages


fb_is_page_management = apps.get_model('b2b', 'fb_is_page_management')
customer_management = apps.get_model('b2b', 'customer_management')


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
        
        # user = api.UsersLookup(screen_name=screen_name)
        # # print(user)
        # for i in user:
        #     print(i)
        
        if len(name) > 1:
            first_name = name.split(" ")[0]
            last_name = name.split(" ")[1]
        else:
            first_name = name.split(" ")[0]
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

def get_facebook_comment(request, fb_page_management):
    # try:
    # user = request.user    
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
        pages_data = graph.get_object("/me/accounts")

       
        # get page access token
        fb_comment_management.objects.all().delete()
        # fb_is_page_management.objects.all().delete()

        for item in pages_data['data']:
            page_token = item['access_token']
            graph_page = facebook.GraphAPI(access_token=page_token)
            try:
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
                            for fbCommentObj in fbCommentData.get("data"):
                                if fbCommentObj.get("message") is not None:
                                    fbCommentManagementObj = fb_comment_management(customer_name=fbPostManagement.customer_name,
                                                created_time=parser.parse(fbCommentObj.get("created_time")),message=fbCommentObj.get("message"),fb_comment_id=fbCommentObj.get("id"),fb_post_ref=fbPostObj)
                                    fbCommentManagementObj.save()
                                    
                                # get sentiment
                                sentiment = get_sentiment(fbCommentManagementObj.message)

                                sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                                fbCommentManagementObj.sentiment = sentiment
                                

                                blob = TextBlob(fbCommentManagementObj.message)
                                l = languages.get(alpha2=blob.detect_language())
                                lang = l.name
                                fbCommentManagementObj.comment_language = lang

                                fbCommentManagementObj.save()

                                print("------------fbCommentObj---------------->")
                                print(fbCommentObj)
                                # get nationality
                                nationality = get_nationality(fbCommentObj['from']['name'])
                                if nationality:
                                    fbCommentManagementObj.nationality = nationality['jurisdiction']
                                    fbCommentManagementObj.nationality_percent = nationality['percent']
                                    fbCommentManagementObj.save()

                                fbReplyData = graph_page.get_object("/" + str(fbCommentManagementObj.fb_comment_id) + "/comments")
                                if fbReplyData['data']:
                                    fbReplyData['data'][0]['from']['id'] == fbCommentManagementObj.fb_post_ref.fb_page.page_id
                                    fbCommentManagementObj.is_replied = True
                                    fbCommentManagementObj.save()
                            
        
            except Exception as e:
                print("-----------------except-------------->")
                print(e)
          
    # except facebook.GraphAPIError as e:
    #     print(e)

    return True


def get_social_account_details(user):

    """
    Method generate uesr data
    :param user: user
    :return: flag
    """

    # get the user social record.

    social_records = UserSocialAuth.objects.filter(user=user)

    if not social_records:
        return False

    for social_record in social_records:

        if social_record.provider == 'facebook':

            # do for facebook
            print('We are facebook !!!')

            facebook_access_token = social_record.extra_data.get('access_token')

            # call facebook graph api
            facebook_graph = facebook.GraphAPI(access_token=facebook_access_token)
            facebook_pages_data = facebook_graph.get_object("/me/accounts")

            pages_data = facebook_pages_data.get('data')
            
            
            if pages_data:
                fb_data = {
                    'data': pages_data,
                    'user': user,
                    'id': social_record.id
                }
                facebook_pages(**fb_data)


                instagram_pages(**fb_data)
            # If data not present in pages_data then delete all pages and account linking to that user account #20-Oct-2020 - Vishakha
            else:
                fb_page = fb_is_page_management.objects.filter(fb_account=social_record.id)
                for page in fb_page:
                    fb_page.delete()
                social_account = UserSocialAuth.objects.get(provider='facebook', id=social_record.id)
                social_account.delete()
                
                


                    

    return True


def instagram_pages(**instagram_data):

    try:
        
        data = instagram_data.get('data')
        user = instagram_data.get('user')
        import requests, random

        user_fb_last = UserSocialAuth.objects.filter(user=user, provider='facebook').last()

        social_accounts = UserSocialAuth.objects.filter(
                provider='instagram', uid=user_fb_last.uid
            )
        for account in social_accounts:
            if account.user != user:
                account.delete()


        for in_data in data:

            access_token = in_data.get('access_token')
            page_id = in_data.get('id')

            insta_api_url = "https://graph.facebook.com/%s/?fields=instagram_business_account&access_token=%s" % (
                page_id, access_token
            )

            insta_data = requests.get(insta_api_url).json()

            if 'instagram_business_account' in insta_data:
                insta_id = insta_data['instagram_business_account']

                get_username_url = "https://graph.facebook.com/%s?fields=username&access_token=%s" % (
                    insta_id['id'], access_token
                )

                username = requests.get(get_username_url).json()

                if username.get('username'):
                    UserSocialAuth.objects.get_or_create(
                        user=user, provider='instagram', uid=user_fb_last.uid,
                        extra_data=user_fb_last.extra_data, 
                    )
            else:
                social_accounts = UserSocialAuth.objects.filter(
                    provider='instagram', uid=user_fb_last.uid
                )
                for account in social_accounts:
                    if account.user != user:
                        account.delete()
                        

    except Exception as e:
        print("--------------insta-exception------------------->")
        print(e.args)

    return True


def facebook_pages(**fb_data):

    try:

        availble_fb_list = []
        user = fb_data.get('user')
        data = fb_data.get('data')
        id = fb_data.get('id')

        customer = customer_management.objects.get(user=user)

        # if data:
   
        for item in data:

            fb_account = UserSocialAuth.objects.filter(user=user, id=id).last()

            fb_pages = fb_is_page_management.objects.filter(
                customer_name=customer, fb_account=fb_account, page_id=item['id']
            )

            availble_fb_list.extend(
                list(fb_pages.values_list('id', flat=True))
            )
        # else:
        #     fb_is_page_management.objects.filter(
        #         customer_name=customer, fb_account=fb_account).delete()    

        # fb_page = fb_is_page_management.objects.filter(customer_name=customer, fb_account=fb_account).exclude(id__in=availble_fb_list)
        # if fb_page.count() == 1:
        #     fb_page = fb_is_page_management.objects.get(id=pk)
        #     social_account = UserSocialAuth.objects.get(provider='facebook', id=fb_page.fb_account.id)
        #     social_account.delete()                
        
        fb_is_page_management.objects.filter(
            customer_name=customer, fb_account=fb_account).exclude(
            id__in=availble_fb_list
        ).delete()


        print(availble_fb_list)
    

    except Exception as e:
        print("------------except555----------------->")
        print(e.args)

    return True