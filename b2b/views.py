from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import messages
from phonebooth import settings
from social_django.models import UserSocialAuth
from .models import *
import twitter
from dateutil import parser
from django.http import JsonResponse, HttpResponse, Http404
from .forms import cannedResponseForm
from .forms import createPersonaForm
from django.template.response import TemplateResponse
from nationality.models import *
from authentication.models import User

from datetime import timedelta, date,datetime
from django.db.models import Count,Sum
from django.utils import timezone

from authentication.utils import get_paginator_items

from django.contrib.auth.decorators import login_required
import requests
from textblob import TextBlob
from iso639 import languages

import facebook

from .utils import facebookComment, twitterComment, allComment, instaComment
# from celery import shared_task

from customer_dashboard.views import SocialMediaPlatform
# from customer_dashboard.models import Profile


class ReportView(TemplateView):
    @login_required
    def reports(request):
        context = {}
        twCommentanswered = 0
        twCommentPositive = 0
        twCommentNegative = 0
        fbComment = 0
        instaComment = 0
        user = request.user
        try:
            customerObj = customer_management.objects.get(user=request.user)
            twPostObj = twitter_post_management.objects.filter(customer_name=customerObj)
            for postObj in twPostObj:
                twCommentObj = twitter_comment_management.objects.filter(twitter_post_ref=postObj, is_replied=False)
                twCommentanswered += twCommentObj.count()

                twCommentObjpositive = twCommentObj.filter(sentiment=1)
                twCommentPositive += twCommentObjpositive.count()

                twCommentObjnegative = twCommentObj.filter(sentiment=2)
                twCommentNegative += twCommentObjnegative.count()


            context = {
                'twComment': twCommentanswered,
                'twCommentpositive': twCommentPositive,
                'twCommentnegative': twCommentNegative,
                'fbComment': fbComment,
                'instaComment' : instaComment
            }
        except Exception as e:
            print("------------------context-exception------------------>")
            print(e)
        return render(request, 'reports/reports.html', context)

    @login_required
    def twitter_report(request, type):
        dataRow = []
        context = {}
        import fasttext
        from django.db.models import Q
        # try:
        customerObj = customer_management.objects.get(user=request.user)
        collectTw = twitter_post_management.objects.filter(customer_name__id=customerObj.id).order_by('-created_time')
        
        if collectTw:
            
            for twObj in collectTw:
                twPostObj = twitter_comment_management.objects.filter(twitter_post_ref=twObj, is_replied=False).order_by('-created_on')
                if type=="unanswered":
                    twPostObj = twPostObj
                elif type=="positive":
                    twPostObj = twitter_comment_management.objects.filter(twitter_post_ref=twObj, sentiment=1).order_by('-created_on')
                elif type=="negative":
                    twPostObj = twitter_comment_management.objects.filter(twitter_post_ref=twObj, sentiment=2).order_by('-created_on')
                elif type=="neutral":
                    twPostObj = twitter_comment_management.objects.filter(twitter_post_ref=twObj, sentiment=3).order_by('-created_on')

                else:
                    twPostObj = twPostObj
                
                if twPostObj:
                    
                    
                    for twCommentObj in twPostObj:
                        try:
                            canned_response = canned_response_management.objects.get(customer_name=customerObj, social_accounts=twCommentObj.twitter_post_ref.twitter_account)
                        except Exception as e:
                            canned_response = None
                            print("-------------------ee--------------->")
                            print(e)
                            # msg = "Please create canned responses."
                            # context["msg"] = msg
                        
                        
                        dataDictRow = {}
                        dataDictRow["id"] = twCommentObj.id
                        dataDictRow["post_tweet"] = twObj.message
                        dataDictRow["comment_id"] = twCommentObj.tweet_reply_id
                        dataDictRow["is_replied"] = twCommentObj.is_replied
                        dataDictRow["created_on"] = twObj.created_time
                        dataDictRow["source"] = "twitter"
                        dataDictRow["comment"] = twCommentObj.message
                        dataDictRow["sent_response"] = twCommentObj.resposne_sent
                        dataDictRow['twitter_post_ref'] = twCommentObj.twitter_post_ref.id
                        dataDictRow['nationality'] = twCommentObj.nationality
                        dataDictRow['location'] = twCommentObj.location
                        dataDictRow['language'] = twCommentObj.comment_language
                        # canned_response = canned_response_management.objects.filter(customer_name=customerObj,social_accounts=twCommentObj.twitter_post_ref.twitter_account)[0]
                        if canned_response and twCommentObj.sentiment:
                            if twCommentObj.sentiment.sentiment == "positive":
                                dataDictRow["canned_response"] = canned_response.positive_response_text

                            elif twCommentObj.sentiment.sentiment == "negative":
                                dataDictRow["canned_response"] = canned_response.negative_response_text
                            elif twCommentObj.sentiment.sentiment == "neutral":
                                dataDictRow["canned_response"] = canned_response.neutral_response_text

                        else:
                            dataDictRow["canned_response"] = "NA"

                        if twCommentObj.sentiment:
                            dataDictRow["sentiment_analysis"] = str(twCommentObj.sentiment.sentiment).upper()
                        
                        dataRow.append(dataDictRow)
                
        # except Exception as e:
        #     print("000000000000000000000000000000000000000000000000")
        #     print(e.args)

        dataRow = get_paginator_items(
        dataRow, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))

        if (request.GET.get('page')):
            pageNo=int(request.GET.get('page'))
        else:
            pageNo=1

        pageNo=(pageNo-1) *10

        context['dataRow'] = dataRow
        context['pageNo'] = pageNo

        
        return render(request, 'reports/twitter_report.html', context)


    @login_required
    def fb_report(request, type):
        # get_facebook_comment(request)
        dataRow = []
        context = {}
        import fasttext
        from django.db.models import Q
        try:
            customerObj = customer_management.objects.get(user=request.user)
            collectfb = fb_post_management.objects.filter(customer_name__id=customerObj.id).order_by('-created_time')
            
            if collectfb:
                for fbObj in collectfb:
                    try:
                        canned_response = canned_response_management.objects.get(customer_name=customerObj, social_accounts=fbObj.fb_account, fb_page=fbObj.fb_page)
                    except Exception as e:
                        canned_response = None
                        print("-------------------ee--------------->")
                        print(e)
                        # msg = "Please create canned responses."
                        # context["msg"] = msg
                    
                    fbPostObj = fb_comment_management.objects.filter(fb_post_ref=fbObj, is_replied=False).order_by('-created_on')
                    if type=="unanswered":
                        fbPostObj = fbPostObj
                    elif type=="positive":
                        fbPostObj = fb_comment_management.objects.filter(fb_post_ref=fbObj, sentiment=1).order_by('-created_on')
                    elif type=="negative":
                        fbPostObj = fb_comment_management.objects.filter(fb_post_ref=fbObj, sentiment=2).order_by('-created_on')
                    elif type=="neutral":
                        fbPostObj = fb_comment_management.objects.filter(fb_post_ref=fbObj, sentiment=3).order_by('-created_on')

                    else:
                        fbPostObj = fbPostObj
                    
                    if fbPostObj:
                        for fbCommentObj in fbPostObj:
                            dataDictRow = {}
                            dataDictRow["id"] = fbCommentObj.id
                            dataDictRow["post_tweet"] = fbCommentObj.fb_post_ref.message
                            dataDictRow["is_replied"] = fbCommentObj.is_replied
                            dataDictRow["created_on"] = fbCommentObj.created_time
                            dataDictRow["source"] = "facebook"
                            dataDictRow["comment"] = fbCommentObj.message
                            dataDictRow["comment_id"] = fbCommentObj.fb_comment_id
                            dataDictRow["sent_response"] = fbCommentObj.resposne_sent
                            dataDictRow['fb_post_ref'] = fbCommentObj.fb_post_ref.id
                            dataDictRow['nationality'] = fbCommentObj.nationality
                            dataDictRow['location'] = fbCommentObj.location
                            dataDictRow['language'] = fbCommentObj.comment_language
                            dataDictRow['fb_page'] = fbCommentObj.fb_post_ref.fb_page.page_name
                           
                            if canned_response and fbCommentObj.sentiment:
                                if fbCommentObj.sentiment.sentiment == "positive":
                                    dataDictRow["canned_response"] = canned_response.positive_response_text

                                elif fbCommentObj.sentiment.sentiment == "negative":
                                    dataDictRow["canned_response"] = canned_response.negative_response_text
                                elif fbCommentObj.sentiment.sentiment == "neutral":
                                    dataDictRow["canned_response"] = canned_response.neutral_response_text

                            else:
                                dataDictRow["canned_response"] = "NA"

                            if fbCommentObj.sentiment:
                                dataDictRow["sentiment_analysis"] = str(fbCommentObj.sentiment.sentiment).upper()
                            
                            dataRow.append(dataDictRow)
                
        except Exception as e:
            print("000000000000000000000000000000000000000000000000")
            print(e.args)

        dataRow = get_paginator_items(
        dataRow, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))

        if (request.GET.get('page')):
            pageNo=int(request.GET.get('page'))
        else:
            pageNo=1

        pageNo=(pageNo-1) *10

        context['dataRow'] = dataRow
        context['pageNo'] = pageNo

        
        return render(request, 'reports/fb_report.html', context)

    @login_required
    def insta_report(request, type):
        dataRow = []
        context = {}
        import fasttext
        from django.db.models import Q
        try:
            customerObj = customer_management.objects.get(user=request.user)
            collectinsta = ig_post_management.objects.filter(customer_name__id=customerObj.id).order_by('-created_time')
            
            if collectinsta:
                for instaObj in collectinsta:
                    try:
                        canned_response = canned_response_management.objects.get(customer_name=customerObj, social_accounts=instaObj.insta_account)
                    except Exception as e:
                        canned_response = None
                        print("-------------------ee--------------->")
                        print(e)
                        # msg = "Please create canned responses."
                        # context["msg"] = msg

                    instaPostObj = ig_comment_management.objects.filter(ig_post_ref=instaObj, is_replied=False).order_by('-created_on')
                    if type=="unanswered":
                        instaPostObj = instaPostObj
                    elif type=="positive":
                        instaPostObj = ig_comment_management.objects.filter(ig_post_ref=instaObj, sentiment=1).order_by('-created_on')
                    elif type=="negative":
                        instaPostObj = ig_comment_management.objects.filter(ig_post_ref=instaObj, sentiment=2).order_by('-created_on')
                    elif type=="neutral":
                        instaPostObj = ig_comment_management.objects.filter(ig_post_ref=instaObj, sentiment=3).order_by('-created_on')

                    else:
                        instaPostObj = instaPostObj
                    
                    if instaPostObj:
                        for instaCommentObj in instaPostObj:
                            dataDictRow = {}
                            dataDictRow["id"] = instaCommentObj.id
                            dataDictRow["post_tweet"] = instaCommentObj.ig_post_ref.message
                            dataDictRow["is_replied"] = instaCommentObj.is_replied
                            dataDictRow["created_on"] = instaCommentObj.created_time
                            dataDictRow["source"] = "instagram"
                            dataDictRow["comment"] = instaCommentObj.message
                            dataDictRow["comment_id"] = instaCommentObj.ig_comment_id
                            dataDictRow["insta_post_ref"] = instaCommentObj.ig_post_ref.id
                            dataDictRow["sent_response"] = instaCommentObj.resposne_sent
                            dataDictRow['nationality'] = instaCommentObj.nationality
                            dataDictRow['location'] = instaCommentObj.location
                            dataDictRow['language'] = instaCommentObj.comment_language
                            
                            if canned_response and instaCommentObj.sentiment:
                                if instaCommentObj.sentiment.sentiment == "positive":
                                    dataDictRow["canned_response"] = canned_response.positive_response_text

                                elif instaCommentObj.sentiment.sentiment == "negative":
                                    dataDictRow["canned_response"] = canned_response.negative_response_text
                                elif instaCommentObj.sentiment.sentiment == "neutral":
                                    dataDictRow["canned_response"] = canned_response.neutral_response_text

                            else:
                                dataDictRow["canned_response"] = "NA"

                            if instaCommentObj.sentiment:
                                dataDictRow["sentiment_analysis"] = str(instaCommentObj.sentiment.sentiment).upper()
                            
                            dataRow.append(dataDictRow)

            print("===============================================>")   
            print(dataRow)
        except Exception as e:
            print("000000000000000000000000000000000000000000000000")
            print(e.args)

        dataRow = get_paginator_items(
        dataRow, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))

        if (request.GET.get('page')):
            pageNo=int(request.GET.get('page'))
        else:
            pageNo=1

        pageNo=(pageNo-1) *10

        context['dataRow'] = dataRow
        context['pageNo'] = pageNo

        
        return render(request, 'reports/insta_report.html', context)

    @login_required
    def putCommentReply(request):
        if request.method == 'POST':
            # getCustomer Chip Details
            chip_id = request.POST.get("chip_id")
            # try:
            customerObj = customer_management.objects.get(user=request.user)
            commentText = request.POST.get("comment")
            commentId = request.POST.get("comment_id")
            if request.POST.get("source") == "facebook":
                comment_id = fb_post_management.objects.get(id=request.POST.get('post_id'), customer_name__user__id=request.POST.get('user_id'))

                graph_page = facebook.GraphAPI(access_token=comment_id.fb_page.user_access_token)

                # commentData = graph_page.put_comment(object_id=comment_id.fb_post_id, message=commentText)
                url = "https://graph.facebook.com/"+commentId+"/comments"

                data = {"access_token": comment_id.fb_page.page_access_token, "message": commentText}

                r = requests.post(url, data = data)

                if "id" in r.text:
                    fb_comment_management.objects.filter(fb_comment_id__exact=commentId).update(is_replied=True, resposne_sent=commentText)
                    return JsonResponse({"success": 1, "message": "Your response has been published on Facebook."})


            if request.POST.get("source") == "instagram":
                comment_id = ig_post_management.objects.get(id=request.POST.get('post_id'), customer_name__user__id=request.POST.get('user_id'))
                
                try:
                    fb_page = fb_is_page_management.objects.get(fb_account__user__id=request.POST.get('user_id'), fb_account__provider="instagram", fb_account=comment_id.insta_account)
                    fb_access_token = fb_page.user_access_token
                except Exception as e:
                    print(e)
                    fb_access_token = ''
                
                    
                
                print("==============commentId=================>")
                print(commentId)

                url_insta_post_comments = "https://graph.facebook.com/v8.0/"+commentId+"/replies"

                data = {"access_token": fb_access_token, "message": commentText}
                headers = {"Content-Type": "application/json"}

                r = requests.post(url_insta_post_comments, data = data, headers=headers)
                

                if "id" in r.text:
                    ig_comment_management.objects.filter(ig_comment_id__exact=commentId).update(is_replied=True, resposne_sent=commentText)
                    return JsonResponse({"success": 1, "message": "Your response has been published on Instagram."})



            if request.POST.get("source") == "twitter":
                # write a code for twitter
                comment_id = twitter_post_management.objects.get(id=request.POST.get('post_id'), customer_name__user__id=request.POST.get('user_id'))
                
                twitter_keys = UserSocialAuth.objects.get(id=comment_id.twitter_account.id)
                
                api = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                                    consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                                    access_token_key=twitter_keys.extra_data['access_token']['oauth_token'],
                                    access_token_secret=twitter_keys.extra_data['access_token']['oauth_token_secret'],
                                    sleep_on_rate_limit=True)
                verifyData = api.VerifyCredentials()
                replyTweet = api.PostUpdate(status=commentText, in_reply_to_status_id=commentId, auto_populate_reply_metadata=True)
                try:
                    twitter_comment_management.objects.filter(tweet_reply_id__exact=commentId, is_replied=False).update(is_replied=True, resposne_sent=commentText)
                    return JsonResponse({"success": 1, "message": "Your response has been published on Twitter."})
                except Exception as e:
                    print("==================rrrr==========================>")
                    print(e.args)

            

            # except Exception as e:
            #     print("===================e====================>")
            #     print(e)

class CannedResponse(TemplateView):
    def add_canned_response_background(request, social_id):
        if social_id:
            try:
                customer = customer_management.objects.get(user=request.user)
            except Exception as e:
                print("-------------------------------->")
                print(e)
            # social_accounts = ''
            try:
                social_accounts = UserSocialAuth.objects.get(pk__exact=social_id)
                if social_accounts.provider == 'facebook':
                    fb_pages = fb_is_page_management.objects.filter(fb_account__id=social_id)
                    for page in fb_pages:
                        data = {
                            "customer_name": customer,
                            "social_accounts": social_accounts,
                            "fb_page": page,
                            "positive_response_text" : '',
                            "neutral_response_text" : '',
                            "negative_response_text" : ''
                        }

                        is_exists = canned_response_management.objects.filter(social_accounts__id=social_id, fb_page=page)
                        if not is_exists:
                            cannedresponse = canned_response_management.objects.create(**data)

                else:
                    data = {
                            "customer_name": customer,
                            "social_accounts": social_accounts,
                            "positive_response_text" : '',
                            "neutral_response_text" : '',
                            "negative_response_text" : ''
                        }
                    
                    cannedresponse = canned_response_management.objects.create(**data)
                obj = canned_response_management.objects.latest('id')
            except Exception as e:
                print("------page-e---------------->")
                print(e)
                social_accounts = ''

        else:
            print("-------------form---------------------->")

        return (obj)

    @login_required
    def cannedResponseList(request):
        try:
            # accounts = UserSocialAuth.objects.get(user_id=request.user.id).all()
            accounts = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider').values('id','provider', 'extra_data')

            dataRow = []
            if accounts:
                for account in accounts:
                    dataDictRow = {}
                    dataDictRow['page_name'] = ''


                    if account['provider'] == 'facebook':
                        fb_pages = fb_is_page_management.objects.filter(fb_account=account['id'], customer_name__user=request.user)
                        for page in fb_pages:
                            dataDictRow = {}
                            canned_responses = canned_response_management.objects.filter(customer_name__user=request.user, social_accounts__id = account['id'], fb_page=page)
                            if canned_responses:
                                for canned_response in canned_responses:
                                    dataDictRow["id"] = canned_response.id
                                    dataDictRow["social_accounts_id"] = account['id']
                                    dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
                                    dataDictRow["positive_response_text"] = canned_response.positive_response_text
                                    dataDictRow["negative_response_text"] = canned_response.negative_response_text
                                    dataDictRow["neutral_response_text"] = canned_response.neutral_response_text
                                    dataDictRow["created_on"] = canned_response.created_on
                                    dataDictRow["source"] = account['provider']
                                    dataDictRow['page_name'] = page.page_name
                            
                            else:
                                canned_response = CannedResponse.add_canned_response_background(request, account['id'])
                                dataDictRow["id"] = canned_response.id
                                dataDictRow["social_accounts_id"] = account['id']
                                dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
                                dataDictRow["positive_response_text"] = canned_response.positive_response_text
                                dataDictRow["negative_response_text"] = canned_response.negative_response_text
                                dataDictRow["neutral_response_text"] = canned_response.neutral_response_text
                                dataDictRow["created_on"] = canned_response.created_on
                                dataDictRow["source"] = account['provider']
                                dataDictRow['page_name'] = page.page_name

                            dataRow.append(dataDictRow)

                    else:
                        canned_responses = canned_response_management.objects.filter(customer_name__user=request.user, social_accounts__id = account['id'])
                        if canned_responses:
                            for canned_response in canned_responses:
                                dataDictRow["id"] = canned_response.id
                                dataDictRow["social_accounts_id"] = account['id']
                                if account['provider'] == 'twitter':
                                    dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
                                if account['provider'] == 'instagram':
                                    dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
                                dataDictRow["positive_response_text"] = canned_response.positive_response_text
                                dataDictRow["negative_response_text"] = canned_response.negative_response_text
                                dataDictRow["neutral_response_text"] = canned_response.neutral_response_text
                                dataDictRow["created_on"] = canned_response.created_on
                                dataDictRow["source"] = account['provider']
                        else:
                            canned_response = CannedResponse.add_canned_response_background(request, account['id'])
                            dataDictRow["social_accounts_id"] = account['id']
                            if account['provider'] == 'twitter':
                                dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
                            if account['provider'] == 'instagram':
                                dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
                            dataDictRow["positive_response_text"] = canned_response.positive_response_text
                            dataDictRow["negative_response_text"] = canned_response.negative_response_text
                            dataDictRow["neutral_response_text"] = canned_response.neutral_response_text
                            dataDictRow["created_on"] = canned_response.created_on
                            dataDictRow["source"] = account['provider']
                            dataDictRow["id"] = canned_response.id
                        dataRow.append(dataDictRow)
                    # return JsonResponse({"success": 1, "message": "Pre-set Reponse deleted"})
        except Exception as e:
            print("-------------------------------->")
            print(e)
        dataRow = get_paginator_items(
            dataRow, settings.DASHBOARD_PAGINATE_BY,
            request.GET.get('page'))

        if (request.GET.get('page')):
            pageNo=int(request.GET.get('page'))
        else:
            pageNo=1
        pageNo = (pageNo - 1) * 10
        ctx = {
            # "pageNo": pageNo,
            "dataRow": dataRow,

        }

        return render(request, "customer/canned_response/list.html", ctx)

    @login_required
    def addCannedReponse(request):
        form = cannedResponseForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                try:
                    customer = customer_management.objects.get(user=request.user)
                except Exception as e:
                    print("-------------------------------->")
                    print(e)
                social_accounts=''
                if request.POST.get('social_accounts'):
                    try:
                        social_accounts = UserSocialAuth.objects.get(pk__exact=request.POST.get("social_accounts"))
                    except Exception as e:
                        social_accounts = ''
                else:
                    social_accounts = ''

                form.cleaned_data['customer_name'] = customer
                form.cleaned_data['social_accounts'] = social_accounts
                canned_response_management.objects.create(**form.cleaned_data)
                # print(form.cleaned_data)
                # form.save()
                # form.cleaned_data['customer']
                msg = "Pre-set Reponse added"
                messages.success(request, msg)
                return redirect("b2b:custom-response")

            else:
                print("-------------form---------------------->")
                print(form.errors)
        
        ctx = {
            "form": form
        }
        return render(request, "customer/canned_response/form.html", ctx)

    def editCannedReponse(request, id):
        try:
            customer = customer_management.objects.get(user=request.user)
        except Exception as e:
            print("-------------------------------->")
            print(e)

        canned_reponse = canned_response_management.objects.get(id=id)
        account = UserSocialAuth.objects.get(pk__exact=canned_reponse.social_accounts.id)

        dataDictRow = {}
        dataRow = []
        dataDictRow["social_accounts_id"] = account.id
        if account.provider == 'facebook':
            dataDictRow['social_accounts_text'] = account.provider.capitalize() + " - " + account.extra_data['name'].capitalize()
            fb_pages = fb_is_page_management.objects.filter(fb_account=account.id)
            for page in fb_pages:
                dataDictRow['page_name'] = page.page_name

        if account.provider == 'twitter':
            dataDictRow['social_accounts_text'] = account.provider.capitalize() + " - " + account.extra_data['access_token']['screen_name'].capitalize()
        if account.provider == 'instagram':
            dataDictRow['social_accounts_text'] = account.provider.capitalize() + " - " + account.extra_data['name'].capitalize()
            # fb_pages = fb_is_page_management.objects.filter(fb_account=account.id)
            # for page in fb_pages:
            #     dataDictRow['page_name'] = page.page_name
        dataRow.append(dataDictRow)
        form = cannedResponseForm(request.POST or None, instance = canned_reponse)

        if request.method == "POST":
            social_accounts = ''
            if request.POST.get('social_accounts'):
                try:
                    social_accounts = UserSocialAuth.objects.get(pk__exact=request.POST.get("social_accounts"))
                except Exception as e:
                    social_accounts = ''
            else:
                social_accounts = ''
            if form.is_valid():
                form.cleaned_data['customer_name'] = customer
                form.cleaned_data['social_accounts'] = social_accounts
                form.save()
                msg = "Custom Reponse updated"
                messages.success(request, msg)
                return redirect("b2b:custom-response")

            else:
 
                print("-------------form---------------------->")
                print(form.errors)

        ctx = {
            "form": form,
            "canned_reponse": canned_reponse,
            "dataDictRow": dataDictRow
        }
        return render(request, "customer/canned_response/form.html", ctx)
        



    @login_required
    def deleteCannedResponse(request, pk):
        try:
            reponse = canned_response_management.objects.get(id = pk)
            if reponse:
                reponse.delete()
                msg = "Pre-set Reponse deleted"
                messages.success(request, msg)
                # return redirect("b2b:canned-response")

        except Exception as e:
            print(e)

        return JsonResponse({"success": 1, "message": "Pre-set Reponse deleted"})

import datetime
def daterange(start_date, end_date):
    end_date = end_date + datetime.timedelta(days=1)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class PersonaView(TemplateView):
    @login_required
    def PersonaListView(request):
        chips = customer_chiptiles.objects.filter(customer_ref__user=request.user)
       
        try:
            customer_id = customer_management.objects.get(user=request.user)
        except Exception as e:
            print(e)
        context = {
            "chips": chips,
            "customer_id": customer_id.id
        }

        return render(request, "persona/list.html", context)

    @login_required
    def PersonaReportView(request):
        chips = customer_chiptiles.objects.filter(customer_ref__user=request.user)

        try:
            customer_id = customer_management.objects.get(user=request.user)
        except Exception as e:
            print(e)
        context = {
            "chips": chips,
            "customer_id": customer_id.id
        }

        return render(request, "persona/preports/new_report.html", context)

    @login_required
    def addCustomerNewChip(request):
        if request.method == 'POST':
            if request.POST.get("customer_id"):
                try:
                    customerObj = customer_management.objects.get(pk__exact=request.POST.get("customer_id"))
                    # customerObj = User.objects.get(pk__exact=request.POST.get("customer_id"))
                except Exception as e:
                    return JsonResponse({"success": 0, "message": "Customer does not available"})


                try:
                    user = User.objects.get(id=request.user.id)
                except Exception as e:
                    print("00000000000000000000000")

            if request.POST.get("customer_chip_title"):
                customer_chip_title = request.POST.get("customer_chip_title")

            if request.POST.get("customer_twitter"):
                customer_twitter = True
            else:
                customer_twitter = False

            if request.POST.get("customer_facebook"):
                customer_facebook = True
            else:
                customer_facebook = False

            if request.POST.get("customer_instagram"):
                customer_instagram = True
            else:
                customer_instagram = False

            if request.POST.get("reports"):
                try:
                    reports = ReportTypeMaster.objects.get(name=request.POST.get("reports"))
                except Exception as e:
                    print(e)
                    reports = None
            else:
                reports = None

            
            if request.POST.get("date_from"):
                date_duration_from = request.POST.get("date_from")
            else:
                date_duration_from = ''

            if request.POST.get("date_to"):
                date_duration_to = request.POST.get("date_to")
            else:
                date_duration_to = ''

            if request.POST.get('sentiment'):
                sentiment = request.POST.get('sentiment')
            else:
                sentiment = ''

            if request.POST.getlist('nationalities'):
                nationalities = ','.join(request.POST.getlist('nationalities'))
            else:
                nationalities = ""
            if request.POST.getlist('locations'):
                locations = ','.join(request.POST.getlist('locations'))
            else:
                locations = ""

        

            if request.POST.get("customer_chip_title") == "":
                return JsonResponse({"success": 0, "message": "Please enter chip title. "})

            if not customer_instagram and not customer_facebook and not customer_twitter:
                return JsonResponse({"success": 0, "message":"Please select atleast one source. "})



        customer_chips = customer_chiptiles.objects.create(
            customer_ref = customerObj,
            chip_title=customer_chip_title,
            capture_facebook=customer_facebook,
            capture_twitter=customer_twitter,
            capture_instagram=customer_instagram,
            user=user,
            report_type = reports,
            date_duration_from = date_duration_from,
            date_duration_to = date_duration_to,
            sentiment = sentiment,
            culture = nationalities,
            location = locations

        )

        # for report_id in report_list:
        #     customer_chips.report_type.add(report)

        # for param_id in params_list:
        #     customer_chips.parameters.add(param_id)


        return JsonResponse({"success": 1, "message": "success"})

    @login_required
    def addNewPersona(request):
        responseDict = {}
        user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            # check whether it's valid:
            if not request.POST.get('customer_chip_title'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter title'
                return JsonResponse(responseDict)

            if not request.POST.get("reportType"):
                responseDict['success'] = 0
                responseDict['message'] = 'Please select Report Type'
                return JsonResponse(responseDict)

            if not request.POST.get('date_from'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter Start Date'
                return JsonResponse(responseDict)

            if not request.POST.get('date_to'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter End Date'
                return JsonResponse(responseDict)
            #  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#
            #  If client approved the validations for below fields then uncommnet the below code   #
            # ''''''''''''''''''''''''''''''''''''''<>'''''''''''''''''''''''''''''''''''''''''''''#
            # if not request.POST.get('social_accounts'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select social accounts'
            #     return JsonResponse(responseDict)

            # if request.POST.get("reportType") == 1 and not request.POST.getlist('locations') and not request.POST.getlist('sentiments') and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast locations, sentiments or cultures'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 2 and not request.POST.getlist('sentiments'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select sentiments'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 3  and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast cultures'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 4 and not request.POST.getlist('locations') and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast locations or cultures'
            #     return JsonResponse(responseDict)

            if request.POST.get("customer_id"):
                try:
                    customerObj = customer_management.objects.get(pk__exact=request.POST.get("customer_id"))
                except Exception as e:
                    return JsonResponse({"success": 0, "message": "Customer does not available"})
            else:
                customerObj = customer_management.objects.get(user__id__exact=request.user.id)

            if request.POST.get("customer_chip_title"):
                customer_chip_title = request.POST.get("customer_chip_title")

            if request.POST.get("reportType"):
                try:
                    reports = ReportTypeMaster.objects.get(id=request.POST.get("reportType"))
                except Exception as e:
                    print(e)
                    reports = ''
            else:
                reports = ''

            if request.POST.get("date_from"):
                date_duration_from = parser.parse(request.POST.get("date_from"))
            else:
                date_duration_from = ''

            if request.POST.get("date_to"):
                date_duration_to = parser.parse(request.POST.get("date_to"))
            else:
                date_duration_to = ''

            if request.POST.getlist('sentiments'):
                try:
                    sentiments = request.POST.getlist("sentiments")
                except Exception as e:
                    sentiments = ''
            else:
                sentiments = ''

            if request.POST.getlist('social_accounts'):
                try:
                    social_accounts = request.POST.getlist("social_accounts")
                except Exception as e:
                    social_accounts = ''
            else:
                social_accounts = ''

            if request.POST.getlist('nationalities'):
                try:
                    nationalities = request.POST.getlist("nationalities")
                except Exception as e:
                    nationalities = ''
            else:
                nationalities = ''

            if request.POST.getlist('locations'):
                try:
                    locations = request.POST.getlist("locations")
                except Exception as e:
                    locations = ''
            else:
                locations = ''

            print("-------------locations-------------------->")
            print(locations)
            if request.POST.get("customer_chip_title") == "":
                return JsonResponse({"success": 0, "message": "Please enter chip title. "})

        try:
       

            if request.POST.get("reports"):
                try:
                    instance = customer_persona.objects.get(
                        id=request.POST.get("reports"),
                        customer_ref=customerObj,
                        user=user
                    )

                
                except Exception as e:
                    print("-----------exxx------------->")
                    print(e)


            else:
                instance = customer_persona.objects.create(
                    customer_ref=customerObj,
                    chip_title=customer_chip_title,
                    user=user,
                    report_type=reports,
                    date_duration_from=date_duration_from,
                    date_duration_to=date_duration_to,
                )

            instance.chip_title = customer_chip_title
            instance.date_duration_from = date_duration_from
            instance.date_duration_to = date_duration_to
            instance.save()


            social_auth_list = []
            if instance.social_auth_id.all():
                for account in instance.social_auth_id.all():
                    for i in social_accounts:
                        if str(account.id) == i:
                            print("---------------if-------------->")
                        else:
                            social_auth_list.append(i)
                    if str(account.id) not in social_accounts:
                        instance.social_auth_id.remove(account)

                accounts = UserSocialAuth.objects.filter(id__in=social_auth_list)
                instance.social_auth_id.add(*accounts)
            else:
                accounts = UserSocialAuth.objects.filter(id__in=social_accounts)
                instance.social_auth_id.add(*accounts)

            sentiment_list = []
            if instance.sentiment_id.all():
                for sentiment in instance.sentiment_id.all():
                    for i in sentiments:
                        if str(sentiment.id) == i:
                            print("---------------if-------------->")
                        else:
                            sentiment_list.append(i)

                        
                    if str(sentiment.id) not in sentiments:
                        instance.sentiment_id.remove(sentiment)

                sentiment = sentimentMaster.objects.filter(id__in=sentiment_list)
                instance.sentiment_id.add(*sentiment)
            
            else:
                sentiments = sentimentMaster.objects.filter(id__in=sentiments)
                instance.sentiment_id.add(*sentiments)


            culture = []
            if instance.culture_id.all(): 
                for cut in instance.culture_id.all():
                    for i in nationalities:
                        if str(cut.id) == i:
                            print("---------------if-------------->")
                        else:
                            culture.append(i)

                        
                    if str(cut.id) not in nationalities:
                        instance.culture_id.remove(cut)
                        
        
                cultures = nationality_prediction.objects.filter(id__in=culture)
                instance.culture_id.add(*cultures)
            
            elif nationalities:
                cultures = nationality_prediction.objects.filter(id__in=nationalities)
                instance.culture_id.add(*cultures)

            location_list = []
            if instance.loaction_id.all():
                for loc in instance.loaction_id.all():
                    for i in locations:
                        if str(loc.id) == i:
                            print("---------------if-------------->")
                        else:
                            location_list.append(i)

                    if str(loc.id) not in locations:
                        instance.loaction_id.remove(loc)

                # fb_location = twitter_comment_management.objects.filter(id__in=location_list)
                # instance.loaction_id.add(*location)

            elif locations:
                comment_locations = persona_location.objects.filter(id__in=locations)
                
                for location in comment_locations:
                    location_list.append(location.location)
                
                # fb_location = fb_comment_management.objects.filter(id__in=locations)
                # if fb_location:
                #     fb_location_obj = fb_comment_management.objects.filter(id__in=locations)
                #     for fb_locationobj in fb_location_obj:
                #         location_list.append(fb_locationobj.location)

                print(location_list)

                for loc in location_list:
                    try:
                        location = persona_location.objects.get(location=loc)
                    except:
                        location = persona_location.objects.create(location=loc)
                    
                    instance.loaction_id.add(location)

           
            if instance:
                return JsonResponse({"success": 1, "message": "success"})
        except Exception as e:
            print("------------------context-exception------------------>")
            print(e)
            return JsonResponse({"success": 1, "message": "Not success","chip_id":instance})

        return JsonResponse({"success": 1, "message": "success"})

    @login_required
    def editPersonaData(request):
        if request.method == 'POST':
            responseDict = {}
            print(request.POST)
            user = User.objects.get(id=request.user.id)
            form = createPersonaForm(request.POST)
            # check whether it's valid:
            if not request.POST.get('chip_title'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter title'
                return JsonResponse(responseDict)

            if not request.POST.get("reportType"):
                responseDict['success'] = 0
                responseDict['message'] = 'Please select Report Type'
                return JsonResponse(responseDict)

            if not request.POST.get('start_date'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter Start Date'
                return JsonResponse(responseDict)

            if not request.POST.get('end_date'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please enter End Date'
                return JsonResponse(responseDict)

            if not request.POST.get('social_accounts'):
                responseDict['success'] = 0
                responseDict['message'] = 'Please select social accounts'
                return JsonResponse(responseDict)

            #  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#
            #  If client approved the validations for below fields then uncommnet the below code   #
            # ''''''''''''''''''''''''''''''''''''''<>'''''''''''''''''''''''''''''''''''''''''''''#

            # if request.POST.get("reportType") == 1 and not request.POST.getlist('locations') and not request.POST.getlist('sentiments') and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast locations, sentiments or cultures'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 2 and not request.POST.getlist('sentiments'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select sentiments'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 3  and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast cultures'
            #     return JsonResponse(responseDict)
            #
            # if request.POST.get("reportType") == 4 and not request.POST.getlist('locations') and not request.POST.getlist('nationalities'):
            #     responseDict['success'] = 0
            #     responseDict['message'] = 'Please select atleast locations or cultures'
            #     return JsonResponse(responseDict)

            if request.POST.get("customer_id"):
                try:
                    customerObj = customer_management.objects.get(pk__exact=request.POST.get("customer_id"))
                except Exception as e:
                    return JsonResponse({"success": 0, "message": "Customer does not available"})

            if form.is_valid():
                chip_title = form.cleaned_data['chip_title']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                if request.POST.get("customer_chip_title"):
                    customer_chip_title = request.POST.get("customer_chip_title")

                if request.POST.get("reportType"):
                    try:
                        reports = ReportTypeMaster.objects.get(id=request.POST.get("reportType"))
                    except Exception as e:
                        print(e)
                        reports = None
                else:
                    reports = None

                if request.POST.get("date_from"):
                    date_duration_from = request.POST.get("date_from")
                else:
                    date_duration_from = ''

                if request.POST.get("date_to"):
                    date_duration_to = request.POST.get("date_to")
                else:
                    date_duration_to = ''

                if request.POST.getlist('sentiments'):
                    try:
                        sentiments = request.POST.getlist("sentiments")
                    except Exception as e:
                        sentiments = None
                else:
                    sentiments = None

                if request.POST.getlist('social_accounts'):
                    try:
                        social_accounts = request.POST.getlist("social_accounts")
                    except Exception as e:
                        social_accounts = None
                else:
                    social_accounts = None

                if request.POST.getlist('nationalities'):
                    try:
                        nationalities = request.POST.getlist("nationalities")
                    except Exception as e:
                        nationalities = None
                else:
                    nationalities = None

                if request.POST.getlist('locations'):
                    try:
                        locations = request.POST.getlist("locations")
                    except Exception as e:
                        locations = None
                else:
                    locations = None

                if request.POST.get("customer_chip_title") == "":
                    return JsonResponse({"success": 0, "message": "Please enter chip title. "})

            try:
                print("------------------context-try------------------>")
                print('e')

                instance = customer_persona.objects.update(

                    customer_ref=customerObj,
                    chip_title=customer_chip_title,
                    user=user,
                    report_type=reports,
                    date_duration_from=date_duration_from,
                    date_duration_to=date_duration_to,
                )
                social_accounts = UserSocialAuth.objects.filter(id__in=social_accounts)
                print("========social_accounts======")
                print(social_accounts)
                print("========social_accounts======")
                instance.social_auth_id.add(*social_accounts)

                sentiment = sentimentMaster.objects.filter(sentiment__in=sentiments)
                instance.sentiment_id.add(*sentiment)

                cultures = nationality_prediction.objects.filter(id__in=nationalities)
                instance.culture_id.add(*cultures)

                location = usa_cities_master.objects.filter(id__in=locations)
                instance.loaction_id.add(*location)

            except:
                messages.error(request, 'Error while creating chip !')
                responseDict['success'] = 0
                responseDict['message'] = 'Error while creating chip'
            else:
                messages.success(request, 'Chip has been created successfully !')
                responseDict['success'] = 1
                responseDict['message'] = 'Chip has been created successfully'
        return JsonResponse(responseDict)

    @login_required
    def editPersonaDetails(request, id):
        personaObj = customer_persona.objects.get(pk__exact=id)
        social_authList = []
        connected_social_accounts = personaObj.social_auth_id.all()
        # connected_social_accounts.values('id', 'provider', 'extra_data')
        if connected_social_accounts:
            for account in connected_social_accounts:
                responseDict = {}
                responseDict['id'] = account.id
                if account.provider == 'facebook':
                    responseDict['text'] = account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
                if account.provider == 'twitter':
                    responseDict['text'] = account.provider.capitalize() + "-" + account.extra_data['access_token']['screen_name'].capitalize()
                if account.provider == 'instagram':
                    responseDict['text'] = account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
                social_authList.append(responseDict)


        cultureList = []
        for val in personaObj.culture_id.all():
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.jurisdiction
            cultureList.append(responseDict)

        locationList = []
        for val in personaObj.loaction_id.all():
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.location
            locationList.append(responseDict)

        sentimentList = []
        for val in personaObj.sentiment_id.all():
            responseDict = {}
            responseDict["id"] = val.id
            responseDict["text"] = val.sentiment
            sentimentList.append(responseDict)


        personaTileModelObj = {
            "chip_id": personaObj.id,
            "chip_title":personaObj.chip_title,
            # "customer_ref":personaObj.customer_ref,
            # "user":personaObj.user,
            "date_duration_from":personaObj.date_duration_from.strftime("%b %d,%Y"),
            "date_duration_to":personaObj.date_duration_to.strftime("%b %d,%Y"),
            "report_type":personaObj.report_type.name,
            "report_type_id":personaObj.report_type.id,
            "cultures":cultureList,
            "social_auth_id":social_authList,
            "locations":locationList,
            "sentiments":sentimentList,
        }
        # msg = "Persona has been edited successfully!"
        # messages.success(request, msg)
        return JsonResponse(personaTileModelObj)

def get_report_type(request):
    responseList = []
    if request.GET["q"] and request.GET["q"] != "":
        reports = ReportTypeMaster.objects.filter(name__icontains=request.GET["q"]).values_list('name', 'name')
    else:
        reports = ReportTypeMaster.objects.all().values_list('name', 'name')
    
    for kay, val in reports:
        responseDict = {}
        responseDict["id"] = kay
        responseDict["text"] = val
        responseList.append(responseDict)
    
    return JsonResponse(responseList, safe=False)

def get_all_report_type(request):
    responseList = []
    reports = ReportTypeMaster.objects.all().values_list('id', 'name')
    for report in reports:
        responseDict = {}
        responseDict["report"] = report
        responseList.append(responseDict)

    print(responseList)
    
    return JsonResponse(responseList, safe=False)


def get_report_title(request,id):
    reports = ReportTypeMaster.objects.values_list( 'name').get(id=id)
    return JsonResponse(reports[0], safe=False)


def get_parameters(request, type):
    responseList = []
    try:
        report = ReportTypeMaster.objects.get(name=type)
    except Exception as e:
        print(e)
        return JsonResponse(responseList, safe=False)
    
    parameters = report.parameters.all().values_list('name', 'name')
    
    for kay, val in parameters:
        responseDict = {}
        responseDict["id"] = kay
        responseDict["text"] = val
        responseList.append(responseDict)
    
    return JsonResponse(responseList, safe=False)


def get_parameters_details(request, id):
    context = {
        'id':id
    }
    return TemplateResponse(request, "persona/include/parameters.html", context)

def get_edit_parameters_details(request, id):
    context = {
        'id':id
    }
    print(context)
    return TemplateResponse(request, "persona/include/parameters1.html", context)

def get_report_details(request, report_type):
    print(report_type.strip())
    responseList = []
    try:
        report = ReportTypeMaster.objects.get(name=report_type.strip())
    except Exception as e:
        print(e)
        context = {}

    parameters = report.parameters.all().values_list('name', 'name')

    for key, val in parameters:
        responseDict = {}
        responseDict["id"] = val
        responseDict["text"] = key.replace("_", " ").title()
        responseList.append(responseDict)

    context = {
        'responseList': responseList,
        'report_type': report_type,
        'id':'2'
    }

    print(context)

    return TemplateResponse(request, "persona/include/parameters_test.html", context)


def get_sentiment(request):
    responseList = []
    # if request.GET["q"] and request.GET["q"] != "":
    #     sentiment = sentimentMaster.objects.filter(sentiment__icontains=request.GET["q"]).values_list('sentiment', 'sentiment')
    # else:
    #     sentiment = sentimentMaster.objects.all().values_list('id','sentiment')

    sentiment = sentimentMaster.objects.all().values_list('id','sentiment')
    for key, val in sentiment:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)


def getNationalitiesList(request):
    if request.GET["q"] and request.GET["q"] != "":
        NATIONALITYOPTIONS = nationality_prediction.objects.distinct('jurisdiction').filter(jurisdiction__icontains=request.GET["q"]).values_list('id','jurisdiction')
    else:
        NATIONALITYOPTIONS = nationality_prediction.objects.distinct('jurisdiction').all().values_list('id', 'jurisdiction')
    responseList = []
    for key, val in NATIONALITYOPTIONS:
        responseDict = {}
        responseDict["id"] = key
        responseDict["text"] = val
        responseList.append(responseDict)
    return JsonResponse(responseList, safe=False)


def getLocationsList(request):
        if request.GET["q"] and request.GET["q"] != "":
            # LOCATIONOPTIONS = usa_cities_master.objects.distinct('city_name').filter(city_name__icontains=request.GET["q"]).values_list('id', 'city_name').order_by('city_name')
            # tw_LOCATIONOPTIONS = twitter_comment_management.objects.filter(location__icontains=request.GET["q"]).distinct('location').values_list('id', 'location').order_by('location')
            # fb_LOCATIONOPTIONS = fb_comment_management.objects.filter(location__icontains=request.GET["q"]).distinct('location').values_list('id', 'location').order_by('location')
            locations = persona_location.objects.filter(location__icontains=request.GET["q"]).values_list('id', 'location').order_by('location')
      
            
        # else:
        #     tw_LOCATIONOPTIONS = None
        #     fb_LOCATIONOPTIONS = None

        responseList = []

        for key, val in locations:
            responseDict = {}
            responseDict["id"] = key
            responseDict["text"] = val
            responseList.append(responseDict)

        # for key, val in tw_LOCATIONOPTIONS:
        #     responseDict = {}
        #     responseDict["id"] = key
        #     responseDict["text"] = val
        #     responseList.append(responseDict)
        return JsonResponse(responseList, safe=False)


def getSocialAccounts(request):
    customerObj = customer_management.objects.get(user__id=request.user.id)
    if request.GET:
       if  request.GET["for"]=='canned':
            if request.GET["type"]=='edit' and request.GET["id"]:
                canned_response = canned_response_management.objects.filter(customer_name=customerObj,social_accounts__id=request.GET["id"]).values('social_accounts')
                social_accounts = UserSocialAuth.objects.filter(user_id=request.user.id,id__in=canned_response).order_by('provider')
            elif request.GET["type"]=='add':
                canned_response = canned_response_management.objects.filter(customer_name=customerObj).values('social_accounts')
                print(canned_response)
                social_accounts = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider').exclude(id__in=canned_response)
       else:
            social_accounts = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider')
    responseList = []
    connected_social_accounts = social_accounts.values('id','provider', 'extra_data')
    if connected_social_accounts:
        for account in connected_social_accounts:
            responseDict = {}
            responseDict['id'] = account['id']
            if  account['provider'] == 'facebook':
                responseDict['text'] = account['provider'].capitalize() + "-" +account['extra_data']['name'].capitalize()
            if  account['provider'] == 'twitter':
                responseDict['text'] = account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
            if  account['provider'] == 'instagram':
                print(account['extra_data'])
                responseDict['text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize()
            responseList.append(responseDict)

    return JsonResponse(responseList, safe=False)

@login_required
def get_persona_report(request, id):
    # try:
    provider = []
    dataRow = []
    # get selected persona details
    # profile = Profile.objects.all()[0]
    # print (profile.avatar_thumbnail.url)    # > /media/avatars/MY-avatar.jpg
    # print (profile.avatar_thumbnail.width)  # > 100
    persona = customer_persona.objects.get(pk__exact=id)
    if request.POST.get("view")=='View Report':
        chip_title = request.POST.getlist("chip_title")
        social_accounts_masterList = request.POST.getlist("social_accounts")
        social_accounts_master = UserSocialAuth.objects.filter(user_id=request.user.id,id__in=social_accounts_masterList).order_by('provider')
        connected_social_accounts = social_accounts_master.values('id', 'provider', 'extra_data')

        locations_masterList = request.POST.getlist("locations")
        try:
            location = persona_location.objects.filter(id__in=locations_masterList).values_list('location')
        except Exception as e:
            location = None

        locations_master_tw = twitter_comment_management.objects.distinct('location').filter(location__in=location).values_list('id', 'location').order_by('location')
       
        locations_master_fb = fb_comment_management.objects.distinct('location').filter(location__in=location).values_list('id', 'location').order_by('location')

        # merge queryset
        from itertools import chain
        locations_master = list(chain(locations_master_tw, locations_master_fb))

        sentiments_masterList = request.POST.getlist("sentiments")
        sentiments_master = sentimentMaster.objects.filter(id__in=sentiments_masterList).values_list('id','sentiment')

        cultures_masterList = request.POST.getlist("nationalities")
        cultures_master = nationality_prediction.objects.distinct('jurisdiction').all().values_list('id','jurisdiction').filter(id__in=cultures_masterList)
        
        social_auth_ids = ''
        cnt = 0
        social_authList = []
        for account in connected_social_accounts:
            if cnt == 0:
                if account['provider'] == 'facebook':
                    social_auth_ids = social_auth_ids + "" + account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize()
                if account['provider'] == 'twitter':
                    social_auth_ids = social_auth_ids + "" + account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
                if account['provider'] == 'instagram':
                    social_auth_ids = social_auth_ids + "" + account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize()
            else:
                if account['provider'] == 'facebook':
                    social_auth_ids = social_auth_ids + " | " + account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize()
                if account['provider'] == 'twitter':
                    social_auth_ids = social_auth_ids + " | " + account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
                if account['provider'] == 'instagram':
                    social_auth_ids = social_auth_ids + " | " + account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize()
            cnt = cnt + 1

        if connected_social_accounts:
            # get all social accounts selected by current user
            for account in connected_social_accounts:
                social_authList.append(account['id'])
        else:
            # get all social accounts connected by current user
            social_accounts = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider')
            for account in social_accounts:
                social_authList.append(account.id)

        cultureList = []
        if cultures_master:
            culture_ids = ''
            cultureList = []
            cnt = 0
            for culture in cultures_master:
                cultureList.append(culture[1])
                if cnt == 0:
                    culture_ids = culture_ids + "" + culture[1].capitalize()
                else:
                    culture_ids = culture_ids + " | " + culture[1].capitalize()
                cnt = cnt + 1
        else:
            culture_ids = ''

        locationList = []
        if locations_master:
            location_ids = ''
            locationList = []
            cnt = 0

            for location in locations_master:
                locationList.append(location[1])
                if cnt == 0:
                    location_ids = location_ids + "" + location[1].capitalize()
                else:
                    location_ids = location_ids + " | " + location[1].capitalize()
                cnt = cnt + 1
        else:
            location_ids = ''

        sentimentList = []
        if sentiments_master:
            sentiment_ids = ''
            cnt = 0
            for sentiment1 in sentiments_master:
                sentimentList.append(sentiment1[0])
                if cnt == 0:
                    sentiment_ids = sentiment_ids + "" + sentiment1[1].capitalize()
                else:
                    sentiment_ids = sentiment_ids + " | " + sentiment1[1].capitalize()
                cnt = cnt + 1
        else:
            sentiment_ids = ''

    else:
        from_date = persona.date_duration_from
        to_date =  persona.date_duration_to

        social_auth_ids = ''
        cnt = 0
        social_authList = []
        for account in persona.social_auth_id.all():
            if cnt == 0:
                if account.provider == 'facebook':
                    social_auth_ids = social_auth_ids+""+account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
                if account.provider == 'twitter':
                    social_auth_ids = social_auth_ids+""+account.provider.capitalize() + "-" + account.extra_data['access_token']['screen_name'].capitalize()
                if account.provider == 'instagram':
                    social_auth_ids = social_auth_ids+""+account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
            else:
                if account.provider == 'facebook':
                    social_auth_ids = social_auth_ids+" | "+account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
                if account.provider == 'twitter':
                    social_auth_ids = social_auth_ids+" | "+account.provider.capitalize() + "-" + account.extra_data['access_token']['screen_name'].capitalize()
                if account.provider == 'instagram':
                    social_auth_ids = social_auth_ids+" | "+account.provider.capitalize() + "-" + account.extra_data['name'].capitalize()
            cnt=cnt+1

        if persona.social_auth_id.all():
            # get all social accounts selected by current user
            for account in persona.social_auth_id.all():
                provider.append(account.provider)
                social_authList.append(account.id)
        else:
            # get all social accounts connected by current user
            social_accounts = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider')
            for account in social_accounts:
                social_authList.append(account.id)

        if 'facebook' in provider:
            socialMediaMOdel = fb_comment_management
        elif 'twitter' in provider:
            socialMediaMOdel = twitter_comment_management
        elif 'instagram' in provider: 
            socialMediaMOdel = ig_comment_management

        cultureList = []
        if persona.culture_id.all():
            culture_ids=''
            cultureList=[]
            cnt = 0
            for culture in persona.culture_id.all():
                cultureList.append(culture.jurisdiction)
                if cnt == 0:
                    culture_ids = culture_ids + "" + culture.jurisdiction.capitalize()
                else:
                    culture_ids = culture_ids + " | " + culture.jurisdiction.capitalize()
                cnt = cnt + 1
        else:
            culture_ids=''

        locationList = []
        if persona.loaction_id.all():
            location_ids = ''
            locationList=[]
            cnt = 0
            for location in persona.loaction_id.all():
                locationList.append(location.location)
                if cnt == 0:
                    location_ids = location_ids + "" + location.location.capitalize()
                else:
                    location_ids = location_ids + " | " + location.location.capitalize()
                cnt=cnt+1
        else:
            location_ids=''
        sentimentList=[]
        if persona.sentiment_id.all():
            sentiment_ids = ''
            cnt = 0
            for sentiment1 in persona.sentiment_id.all():
                sentimentList.append(sentiment1.id)
                if cnt==0:
                    sentiment_ids=sentiment_ids+""+sentiment1.sentiment.capitalize()
                else:
                    sentiment_ids = sentiment_ids + " | " + sentiment1.sentiment.capitalize()
                cnt=cnt+1
        else:
            sentiment_ids=''

    if request.POST.get("view"):
        from_date=f_date = parser.parse(request.POST.get("date_from"))
        to_date=t_date = parser.parse(request.POST.get("date_to"))
    else:
        from_date = persona.date_duration_from
        to_date = persona.date_duration_to

    #Date range is not taking to date so we need to set to date with EOD
    import datetime
    from_date = datetime.datetime(from_date.year, from_date.month,from_date.day,00,00,00)
    to_date = datetime.datetime(to_date.year, to_date.month, to_date.day,23,59,59)

    if 'facebook' in provider:
        dataRow, mylist, scale, CommentObj = facebookComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date)

    if 'instagram' in provider:
        dataRow, mylist, scale, CommentObj = instaComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date)

    if 'twitter' in provider:
        dataRow, mylist, scale, CommentObj = twitterComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date)

    if not provider:
        dataRow, mylist, scale, CommentObj = allComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date)

    if not request.POST.get("export"):
        
        dataRow = get_paginator_items(
            dataRow, settings.DASHBOARD_PAGINATE_BY,
            request.GET.get('page'))
        
        print("==================pge=================>")
        print(dataRow)

   
    
    if (request.GET.get('page')):
        pageNo=int(request.GET.get('page'))
    else:
        pageNo=1

    pageNo=(pageNo-1) *10

    No_data = False
    for i in mylist:
        d = [None, 0, 0, 0]
        if (set(i) == set(d)):
            No_data = True


    context = {
        "CommentObj": CommentObj,
        "sentiment_ids":sentiment_ids,
        "culture_ids":culture_ids,
        "location_ids":location_ids,
        "social_auth_ids":social_auth_ids,
        "mydata": mylist,
        "persona": persona,
        "Positive": True,
        "scale":scale,
        "dataRow":dataRow,
        "pageNo":pageNo,
        "date_duration_from": persona.date_duration_from.strftime("%b %d, %Y"),
        "date_duration_to": persona.date_duration_to.strftime("%b %d, %Y"),
        "from_date": from_date.strftime("%b %d, %Y"),
        "to_date": to_date.strftime("%b %d, %Y"),
        "No_data": No_data,
        # "profile": profile
    }

    if request.POST.get("export"):
        excel = exportExcel(request, context, persona.report_type.id)
        return excel

    
    # except Exception as e:
    #     print("-----------excpt--------------->")
    #     print(e)
    
    if persona.report_type.id == 1 or persona.report_type.id ==2:
        return render(request, "persona/preports/chart_report.html", context)
    if persona.report_type.id == 3 or persona.report_type.id == 4 or persona.report_type.id == 5:
        return render(request, "persona/preports/table_report.html", context)

from .excel import write_excel
from openpyxl.writer.excel import save_virtual_workbook

def exportExcel(request, data, report_type):
    export_data = write_excel(request, data, report_type)
    csv_response = HttpResponse(save_virtual_workbook(export_data), content_type='application/vnd.ms-excel; charset=utf-8')
    csv_response['Content-Disposition'] = 'attachment; filename="Report.xlsx"'

    return csv_response

@login_required
def deletePersonaDetails(request, id):
    try:
        personaObj = customer_persona.objects.get(pk__exact=id)
        deleted = personaObj.delete()
        if deleted:
            msg = "Persona has been deleted successfully!"
            messages.success(request, msg)
            return JsonResponse({"success":1 ,"Message":"Deleted Successfully"})
        else:
            msg = "Deleteion Unsuccessfull!"
            messages.success(request, msg)
            return JsonResponse({"success": 0, "Message": "Deleteion Unsuccessfull"})
    except Exception as e:
        print(e)


def get_nationality(name):
    payload = {}
    headers = {}
    name = name.split(" ")
    if len(name) > 2:
        first_name = name[0]
        last_name = name[2]
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

# @shared_task
def get_facebook_comment(request):
    fb_comment_management.objects.all().delete()
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
        
        # fb_is_page_management.objects.all().delete()

        for item in pages_data['data']:
            # create page
            
            # fb_page_management = fb_is_page_management.objects.create(customer_name=customer,user_access_token=account.extra_data['access_token'], page_access_token=item['access_token'], page_name=item['name'], page_id=item['id'],fb_account=account)
            # fb_page_management.save()
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
            try:
                fbData = graph_page.get_object("/"+item['id']+"/posts/?limit=25")
                
                # 102301934947798_103722898139035/?fields=coordinates,icon,full_picture,message,picture,place,parent_id
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

                    # fbCommentData = graph_page.get_object(fbPostManagement.fb_post_id, fields = "comments")
                
                    if fbCommentData.get('data'):
                        if len(fbCommentData.get('data')) > 0:
                            for fbCommentObj in fbCommentData.get("data"):
                                if fbCommentObj.get("message") is not None:
                                    fbCommentManagementObj = fb_comment_management(customer_name=fbPostManagement.customer_name,
                                                created_time=parser.parse(fbCommentObj.get("created_time")),message=fbCommentObj.get("message"),fb_comment_id=fbCommentObj.get("id"),fb_post_ref=fbPostObj)
                                    fbCommentManagementObj.save()
                    
                                # get sentiment
                                sentiment = SocialMediaPlatform.get_sentiment(fbCommentManagementObj.message)

                                sentiment = sentimentMaster.objects.get(sentiment=sentiment)
                                fbCommentManagementObj.sentiment = sentiment
                                
                                # get location
                                location_url = "https://graph.facebook.com/v8.0/"+item['id']+"?fields=location&access_token="+item['access_token']

                                get_location_url = requests.get(location_url).json()
                                
                                if 'location' in get_location_url:
                                    lat = None
                                    lon = None
                                    location = get_location_url['location']['city'] +', '+get_location_url['location']['country']
                                    if 'latitude' in get_location_url['location']:
                                        lat = get_location_url['location']['latitude']
                                    if 'longitude' in get_location_url['location']:
                                        lon = get_location_url['location']['longitude']
                                    fbCommentManagementObj.location = location
                                    fbCommentManagementObj.location_lat = lat
                                    fbCommentManagementObj.location_lon = lon

                                # get languages
                                blob = TextBlob(fbCommentManagementObj.message)
                                l = languages.get(alpha2=blob.detect_language())
                                lang = l.name
                                fbCommentManagementObj.comment_language = lang

                                fbCommentManagementObj.save()

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

    return HttpResponse("ok")