from b2b.models import fb_comment_management, twitter_comment_management,fb_is_page_management, ig_comment_management
from django.db.models import Count,Sum
from datetime import timedelta, date,datetime
from itertools import chain
from dateutil import parser


import datetime
def daterange(start_date, end_date):
    end_date = end_date + datetime.timedelta(days=1)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def instaComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date):
    if persona.report_type.id == 1:
        CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        if sentimentList and locationList and cultureList :
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList and locationList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])
        elif sentimentList and cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList and cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in=social_authList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        elif cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Last week's daily culture sentiments
    elif persona.report_type.id == 2:
        CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        print("----------------CommentObj-------------------->")
        print(CommentObj)
        if sentimentList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,ig_post_ref__insta_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise happiness quotient
    elif persona.report_type.id == 3:
        CommentObj = ig_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )
        if locationList and cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList :
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise languages comment count
    elif persona.report_type.id == 4 or persona.report_type.id == 5:
        CommentObj = ig_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(ig_post_ref__insta_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])
        
        if locationList and cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
            # fb_post_ref__fb_account__in = social_authList,
        else:
            CommentObj = CommentObj
    else:
        CommentObj = ig_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location').annotate(dcount=Count('created_time')).filter(sentiment_id__isnull=False)


    start_date = date(persona.date_duration_from.year, persona.date_duration_from.month, persona.date_duration_from.day)
    end_date = date(persona.date_duration_to.year, persona.date_duration_to.month,persona.date_duration_to.day)
    vas = []


    mylist = []
    dataRow = []
    scale = ''
    from_date = ''
    to_date = ''
    if request.POST.get("view"):
        from_date = request.POST.get("date_from")
        to_date = request.POST.get("date_to")
        f_date = parser.parse(from_date)
        t_date = parser.parse(to_date)
        newDateRange = daterange(f_date, t_date)

    else:
        newDateRange = daterange(start_date, end_date)

    # Report for Daily social media wise comments count
    if persona.report_type.id == 1 and CommentObj:
        scale = "Date Period"
        for single_date in newDateRange:
            myarray = {}
            positiveCnt=0
            negativeCnt=0
            neutralCnt=0
            for twComment in CommentObj:
                if twComment[1].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                    if twComment [0] == 1:
                        positiveCnt=positiveCnt+twComment[2]

                    if twComment[0] == 2:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment [0] == 3 :
                        neutralCnt=neutralCnt+twComment[2]
                myarray[0]=single_date.strftime("%d %b")
                myarray[1]=positiveCnt
                myarray[2]=negativeCnt
                myarray[3]=neutralCnt
            mylist.append(list(myarray.values()))

    # Report for Last week's daily culture sentiments
    elif persona.report_type.id == 2  and CommentObj:
        scale = "Country"
        countries = []
        for twComment in CommentObj:
            countries.append(twComment[1])
        countriesList=list(set(countries))
        for country in countriesList:
            myarray = {}
            positiveCnt = 0
            negativeCnt = 0
            neutralCnt = 0
            for twComment in CommentObj:
                if twComment[1] == country:
                    if twComment[0] == 1 and twComment[2]:
                        positiveCnt = positiveCnt + twComment[2]

                    if twComment[0] == 2 and twComment[2]:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment[0] == 3 and twComment[2]:
                        neutralCnt = neutralCnt + twComment[2]

                    myarray[0] = country
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
            mylist.append(list(myarray.values()))
            
    # Report for Location wise happiness quotient
    elif persona.report_type.id == 3  and CommentObj:
        scale = "Date Period"
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        for single_date in newDateRange:
            for location in locationsList:
                myarray = {}
                positiveCnt = 0
                negativeCnt = 0
                neutralCnt = 0
                cultureName=''
                for twComment in CommentObj:
                    if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                        if location == twComment[3]:
                            if twComment[0] == 1 and twComment[4]:
                                positiveCnt = positiveCnt + twComment[4]

                            if twComment[0] == 2 and twComment[4]:
                                negativeCnt = negativeCnt + twComment[4]

                            if twComment[0] == 3 and twComment[4]:
                                neutralCnt = neutralCnt + twComment[4]
                            cultureName=twComment[1]
                total = positiveCnt + negativeCnt + neutralCnt
                if total > 0:
                    myarray[0] = single_date.strftime("%b %d, %Y")
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
                    myarray[4] = total
                    myarray[5] = single_date.strftime("%A")
                    myarray[6] = location
                    myarray[7] = cultureName
                    mylist.append(list(myarray.values()))

        dataRow = []
        
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[5]
                dataDictRow["location"] = val[6]
                dataDictRow["culture"] = val[7]
                happy_comments = 0
                negative_comments = 0
                neutral_comments = 0
                if val[4] !=0:
                    happy_comments = val[1] / val[4] * 100
                    negative_comments = val[2] / val[4] * 100
                    neutral_comments = val[3] / val[4] * 100
                dataDictRow["happy_comments"] = '{0:.2f}'.format(happy_comments)
                dataDictRow["negative_comments"] = '{0:.2f}'.format(negative_comments)
                dataDictRow["neutral_comments"] = '{0:.2f}'.format(neutral_comments)
                dataRow.append(dataDictRow)

    # Report for Location wise languages comment counts
    elif persona.report_type.id == 4 or persona.report_type.id == 5 and CommentObj:
        scale = ""
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        languages=[]
        for twComment in CommentObj:
            languages.append(twComment[0])
        languagesList = list(set(languages))

        mylist = []
        for single_date in newDateRange:
            for location in locationsList:
                for language in languagesList:
                    myarray = {}
                    commentCnt = 0
                    for twComment in CommentObj:
                        if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d") :
                            if location == twComment[3] and language == twComment[0]:
                                if twComment[4]:
                                    commentCnt = commentCnt + twComment[4]
                                    myarray[0] = single_date.strftime("%b %d, %Y")
                                    myarray[2] = single_date.strftime("%A")
                                    myarray[3] = twComment[3]
                                    myarray[4] = twComment[1]
                                    myarray[5] = twComment[0]
                                    myarray[1] = commentCnt

                    if myarray:
                        mylist.append(list(myarray.values()))


        dataRow = []
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[2]
                dataDictRow["location"] = val[3]
                dataDictRow["culture"] = val[4]
                dataDictRow["language"] = val[5]
                dataDictRow["comments_count"] = val[1]
                dataRow.append(dataDictRow)

    return dataRow, mylist, scale, CommentObj

def facebookComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date):
    # Query for Daily social media wise comments count
    if persona.report_type.id == 1:
        CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        if sentimentList and locationList and cultureList :
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList and locationList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])
        elif sentimentList and cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList and cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in=social_authList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        elif cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Last week's daily culture sentiments
    elif persona.report_type.id == 2:
        CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        if sentimentList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,fb_post_ref__fb_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise happiness quotient
    elif persona.report_type.id == 3:
        CommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )
        if locationList and cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList :
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise happiness quotient
    elif persona.report_type.id == 3:
        CommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )
        if locationList and cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList :
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])


    # Query for Location wise languages comment count
    elif persona.report_type.id == 4 or persona.report_type.id == 5:
        CommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(fb_post_ref__fb_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])
        
        if locationList and cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
            # fb_post_ref__fb_account__in = social_authList,
        else:
            CommentObj = CommentObj
    else:
        CommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location').annotate(dcount=Count('created_time')).filter(sentiment_id__isnull=False)

    start_date = date(persona.date_duration_from.year, persona.date_duration_from.month, persona.date_duration_from.day)
    end_date = date(persona.date_duration_to.year, persona.date_duration_to.month,persona.date_duration_to.day)
    vas = []


    mylist = []
    dataRow = []
    scale = ''
    from_date = ''
    to_date = ''
    if request.POST.get("view"):
        from_date = request.POST.get("date_from")
        to_date = request.POST.get("date_to")
        f_date = parser.parse(from_date)
        t_date = parser.parse(to_date)
        newDateRange = daterange(f_date, t_date)

    else:
        newDateRange = daterange(start_date, end_date)

    # Report for Daily social media wise comments count
    if persona.report_type.id == 1 and CommentObj:
        scale = "Date Period"
        for single_date in newDateRange:
            myarray = {}
            positiveCnt=0
            negativeCnt=0
            neutralCnt=0
            for twComment in CommentObj:
                if twComment[1].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                    if twComment [0] == 1:
                        positiveCnt=positiveCnt+twComment[2]

                    if twComment[0] == 2:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment [0] == 3 :
                        neutralCnt=neutralCnt+twComment[2]
                myarray[0]=single_date.strftime("%d %b")
                myarray[1]=positiveCnt
                myarray[2]=negativeCnt
                myarray[3]=neutralCnt
            mylist.append(list(myarray.values()))

    # Report for Last week's daily culture sentiments
    elif persona.report_type.id == 2  and CommentObj:
        scale = "Country"
        countries = []
        for twComment in CommentObj:
            countries.append(twComment[1])
        countriesList=list(set(countries))
        for country in countriesList:
            myarray = {}
            positiveCnt = 0
            negativeCnt = 0
            neutralCnt = 0
            for twComment in CommentObj:
                if twComment[1] == country:
                    if twComment[0] == 1 and twComment[2]:
                        positiveCnt = positiveCnt + twComment[2]

                    if twComment[0] == 2 and twComment[2]:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment[0] == 3 and twComment[2]:
                        neutralCnt = neutralCnt + twComment[2]

                    myarray[0] = country
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
            mylist.append(list(myarray.values()))
            
    # Report for Location wise happiness quotient
    elif persona.report_type.id == 3  and CommentObj:
        scale = "Date Period"
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        for single_date in newDateRange:
            for location in locationsList:
                myarray = {}
                positiveCnt = 0
                negativeCnt = 0
                neutralCnt = 0
                cultureName=''
                for twComment in CommentObj:
                    if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                        if location == twComment[3]:
                            if twComment[0] == 1 and twComment[4]:
                                positiveCnt = positiveCnt + twComment[4]

                            if twComment[0] == 2 and twComment[4]:
                                negativeCnt = negativeCnt + twComment[4]

                            if twComment[0] == 3 and twComment[4]:
                                neutralCnt = neutralCnt + twComment[4]
                            cultureName=twComment[1]
                total = positiveCnt + negativeCnt + neutralCnt
                if total > 0:
                    myarray[0] = single_date.strftime("%b %d, %Y")
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
                    myarray[4] = total
                    myarray[5] = single_date.strftime("%A")
                    myarray[6] = location
                    myarray[7] = cultureName
                    mylist.append(list(myarray.values()))

        dataRow = []
        
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[5]
                dataDictRow["location"] = val[6]
                dataDictRow["culture"] = val[7]
                happy_comments = 0
                negative_comments = 0
                neutral_comments = 0
                if val[4] !=0:
                    happy_comments = val[1] / val[4] * 100
                    negative_comments = val[2] / val[4] * 100
                    neutral_comments = val[3] / val[4] * 100
                dataDictRow["happy_comments"] = '{0:.2f}'.format(happy_comments)
                dataDictRow["negative_comments"] = '{0:.2f}'.format(negative_comments)
                dataDictRow["neutral_comments"] = '{0:.2f}'.format(neutral_comments)
                dataRow.append(dataDictRow)

    # Report for Location wise languages comment counts
    elif persona.report_type.id == 4 or persona.report_type.id == 5 and CommentObj:
        scale = ""
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        languages=[]
        for twComment in CommentObj:
            languages.append(twComment[0])
        languagesList = list(set(languages))

        mylist = []
        for single_date in newDateRange:
            for location in locationsList:
                for language in languagesList:
                    myarray = {}
                    commentCnt = 0
                    for twComment in CommentObj:
                        if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d") :
                            if location == twComment[3] and language == twComment[0]:
                                if twComment[4]:
                                    commentCnt = commentCnt + twComment[4]
                                    myarray[0] = single_date.strftime("%b %d, %Y")
                                    myarray[2] = single_date.strftime("%A")
                                    myarray[3] = twComment[3]
                                    myarray[4] = twComment[1]
                                    myarray[5] = twComment[0]
                                    myarray[1] = commentCnt

                    if myarray:
                        mylist.append(list(myarray.values()))


        dataRow = []
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[2]
                dataDictRow["location"] = val[3]
                dataDictRow["culture"] = val[4]
                dataDictRow["language"] = val[5]
                dataDictRow["comments_count"] = val[1]
                dataRow.append(dataDictRow)

    return dataRow, mylist, scale, CommentObj

def twitterComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date):
    # Query for Daily social media wise comments count
    if persona.report_type.id == 1:
        CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        if sentimentList and locationList and cultureList :
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList and locationList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])
        elif sentimentList and cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList and cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif sentimentList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in=social_authList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        elif cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Last week's daily culture sentiments
    elif persona.report_type.id == 2:
        CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        if sentimentList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,twitter_post_ref__twitter_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise happiness quotient
    elif persona.report_type.id == 3:
        CommentObj = twitter_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )
        if locationList and cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList :
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

    # Query for Location wise languages comment count
    elif persona.report_type.id == 4 or persona.report_type.id == 5:
        CommentObj = twitter_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(twitter_post_ref__twitter_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])
        if locationList and cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif locationList:
            CommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
        elif cultureList:
            CommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
            # twitter_post_ref__twitter_account__in = social_authList,
        else:
            CommentObj = CommentObj
    else:
        CommentObj = twitter_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location').annotate(dcount=Count('created_time')).filter(sentiment_id__isnull=False)

    start_date = date(persona.date_duration_from.year, persona.date_duration_from.month, persona.date_duration_from.day)
    end_date = date(persona.date_duration_to.year, persona.date_duration_to.month,persona.date_duration_to.day)
    vas = []


    mylist = []
    dataRow = []
    scale = ''
    from_date = ''
    to_date = ''
    if request.POST.get("view"):
        from_date = request.POST.get("date_from")
        to_date = request.POST.get("date_to")
        f_date = parser.parse(from_date)
        t_date = parser.parse(to_date)
        newDateRange = daterange(f_date, t_date)

    else:
        newDateRange = daterange(start_date, end_date)

    # Report for Daily social media wise comments count
    if persona.report_type.id == 1 and CommentObj:
        scale = "Date Period"
        for single_date in newDateRange:
            myarray = {}
            positiveCnt=0
            negativeCnt=0
            neutralCnt=0
            for twComment in CommentObj:
                if twComment[1].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                    if twComment [0] == 1:
                        positiveCnt=positiveCnt+twComment[2]

                    if twComment[0] == 2:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment [0] == 3 :
                        neutralCnt=neutralCnt+twComment[2]
                myarray[0]=single_date.strftime("%d %b")
                myarray[1]=positiveCnt
                myarray[2]=negativeCnt
                myarray[3]=neutralCnt
            mylist.append(list(myarray.values()))

    # Report for Last week's daily culture sentiments
    elif persona.report_type.id == 2  and CommentObj:
        scale = "Country"
        countries = []
        for twComment in CommentObj:
            countries.append(twComment[1])
        countriesList=list(set(countries))
        for country in countriesList:
            myarray = {}
            positiveCnt = 0
            negativeCnt = 0
            neutralCnt = 0
            for twComment in CommentObj:
                if twComment[1] == country:
                    if twComment[0] == 1 and twComment[2]:
                        positiveCnt = positiveCnt + twComment[2]

                    if twComment[0] == 2 and twComment[2]:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment[0] == 3 and twComment[2]:
                        neutralCnt = neutralCnt + twComment[2]

                    myarray[0] = country
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
            mylist.append(list(myarray.values()))
            
    # Report for Location wise happiness quotient
    elif persona.report_type.id == 3  and CommentObj:
        scale = "Date Period"
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        for single_date in newDateRange:
            for location in locationsList:
                myarray = {}
                positiveCnt = 0
                negativeCnt = 0
                neutralCnt = 0
                cultureName=''
                for twComment in CommentObj:
                    if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                        if location == twComment[3]:
                            if twComment[0] == 1 and twComment[4]:
                                positiveCnt = positiveCnt + twComment[4]

                            if twComment[0] == 2 and twComment[4]:
                                negativeCnt = negativeCnt + twComment[4]

                            if twComment[0] == 3 and twComment[4]:
                                neutralCnt = neutralCnt + twComment[4]
                            cultureName=twComment[1]
                total = positiveCnt + negativeCnt + neutralCnt
                if total > 0:
                    myarray[0] = single_date.strftime("%b %d, %Y")
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
                    myarray[4] = total
                    myarray[5] = single_date.strftime("%A")
                    myarray[6] = location
                    myarray[7] = cultureName
                    mylist.append(list(myarray.values()))

        dataRow = []
        
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[5]
                dataDictRow["location"] = val[6]
                dataDictRow["culture"] = val[7]
                happy_comments = 0
                negative_comments = 0
                neutral_comments = 0
                if val[4] !=0:
                    happy_comments = val[1] / val[4] * 100
                    negative_comments = val[2] / val[4] * 100
                    neutral_comments = val[3] / val[4] * 100
                dataDictRow["happy_comments"] = '{0:.2f}'.format(happy_comments)
                dataDictRow["negative_comments"] = '{0:.2f}'.format(negative_comments)
                dataDictRow["neutral_comments"] = '{0:.2f}'.format(neutral_comments)
                dataRow.append(dataDictRow)

    # Report for Location wise languages comment counts
    elif persona.report_type.id == 4 or persona.report_type.id == 5 and CommentObj:
        scale = ""
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        languages=[]
        for twComment in CommentObj:
            languages.append(twComment[0])
        languagesList = list(set(languages))

        mylist = []
        for single_date in newDateRange:
            for location in locationsList:
                for language in languagesList:
                    myarray = {}
                    commentCnt = 0
                    for twComment in CommentObj:
                        if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d") :
                            if location == twComment[3] and language == twComment[0]:
                                if twComment[4]:
                                    commentCnt = commentCnt + twComment[4]
                                    myarray[0] = single_date.strftime("%b %d, %Y")
                                    myarray[2] = single_date.strftime("%A")
                                    myarray[3] = twComment[3]
                                    myarray[4] = twComment[1]
                                    myarray[5] = twComment[0]
                                    myarray[1] = commentCnt

                    if myarray:
                        mylist.append(list(myarray.values()))


        dataRow = []
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[2]
                dataDictRow["location"] = val[3]
                dataDictRow["culture"] = val[4]
                dataDictRow["language"] = val[5]
                dataDictRow["comments_count"] = val[1]
                dataRow.append(dataDictRow)
  
    return dataRow, mylist, scale, CommentObj


def allComment(request, social_authList, sentimentList, cultureList, locationList, persona, from_date, to_date):
    # if persona.report_type.id == 1:
    # Query for Daily social media wise comments count
    if persona.report_type.id == 1:
        twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
        
        if sentimentList and locationList and cultureList :
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif sentimentList and locationList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,
            created_time__range=[from_date,to_date])

        elif sentimentList and cultureList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,nationality__in=cultureList,sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif locationList and cultureList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList,nationality__in=cultureList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif locationList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(fb_post_ref__fb_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(twitter_post_ref__twitter_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(ig_post_ref__insta_account__in = social_authList,location__in=locationList, sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif sentimentList:

            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])
            
            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(sentiment_id__in=sentimentList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])


        elif cultureList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','created_time',Count('sentiment')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in=social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        CommentObj = list(chain(twCommentObj, fbCommentObj, instaCommentObj))


    # Query for Last week's daily culture sentiments
    elif persona.report_type.id == 2:
        fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])



        if sentimentList:
            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,fb_post_ref__fb_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,twitter_post_ref__twitter_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality',Count('nationality')).order_by('nationality').filter(sentiment_id__in=sentimentList,ig_post_ref__insta_account__in = social_authList, sentiment_id__isnull=False,created_time__range=[from_date, to_date])

        CommentObj = list(chain(twCommentObj, fbCommentObj, instaCommentObj))


    # Query for Location wise happiness quotient
    elif persona.report_type.id == 3:
        twCommentObj = twitter_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )

        fbCommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )

        instaCommentObj = ig_comment_management.objects.all().order_by('created_time').values_list('sentiment_id','nationality','created_time','location',Count('created_time')).filter(ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date] )

        if locationList and cultureList:
            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif locationList :
            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif cultureList:
            twCommentObj = twitter_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            fbCommentObj = fb_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('sentiment_id','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date, to_date])


        CommentObj = list(chain(twCommentObj, fbCommentObj, instaCommentObj))


    # Query for Location wise languages comment count
    elif persona.report_type.id == 4 or persona.report_type.id == 5:
        twCommentObj = twitter_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(twitter_post_ref__twitter_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])

        fbCommentObj = fb_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(fb_post_ref__fb_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])

        instaCommentObj = ig_comment_management.objects.all().order_by('created_time').values_list('comment_language','nationality','created_time','location',Count('created_time')).filter(ig_post_ref__insta_account__in = social_authList,comment_language__isnull=False,created_time__range=[from_date, to_date])

        if locationList and cultureList:
            twCommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            fbCommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif locationList:
            twCommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            fbCommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(location__in=locationList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        elif cultureList:
            twCommentObj = twitter_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,twitter_post_ref__twitter_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])
            # twitter_post_ref__twitter_account__in = social_authList,
       
            fbCommentObj = fb_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,fb_post_ref__fb_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

            instaCommentObj = ig_comment_management.objects.all().values_list('comment_language','nationality','created_time','location',Count('created_time')).order_by('created_time').filter(nationality__in=cultureList,ig_post_ref__insta_account__in = social_authList,sentiment_id__isnull=False,created_time__range=[from_date,to_date])

        CommentObj = list(chain(twCommentObj, fbCommentObj, instaCommentObj))

    start_date = date(persona.date_duration_from.year, persona.date_duration_from.month, persona.date_duration_from.day)
    end_date = date(persona.date_duration_to.year, persona.date_duration_to.month,persona.date_duration_to.day)
    vas = []

    mylist = []
    dataRow = []
    scale = ''
    from_date = ''
    to_date = ''
    if request.POST.get("view"):
        from_date = request.POST.get("date_from")
        to_date = request.POST.get("date_to")
        f_date = parser.parse(from_date)
        t_date = parser.parse(to_date)
        newDateRange = daterange(f_date, t_date)

    else:
        newDateRange = daterange(start_date, end_date)

    # Report for Daily social media wise comments count
    if persona.report_type.id == 1 and CommentObj:
        scale = "Date Period"
        for single_date in newDateRange:
            myarray = {}
            positiveCnt=0
            negativeCnt=0
            neutralCnt=0
            for twComment in CommentObj:
                if twComment[1].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                    if twComment [0] == 1:
                        positiveCnt=positiveCnt+twComment[2]

                    if twComment[0] == 2:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment [0] == 3 :
                        neutralCnt=neutralCnt+twComment[2]
                myarray[0]=single_date.strftime("%b %d")
                myarray[1]=positiveCnt
                myarray[2]=negativeCnt
                myarray[3]=neutralCnt
            mylist.append(list(myarray.values()))

    if persona.report_type.id == 2 and CommentObj:
        scale = "Country"
        countries = []
        for twComment in CommentObj:
            countries.append(twComment[1])
        countriesList=list(set(countries))
        for country in countriesList:
            myarray = {}
            positiveCnt = 0
            negativeCnt = 0
            neutralCnt = 0
            for twComment in CommentObj:
                if twComment[1] == country:
                    if twComment[0] == 1 and twComment[2]:
                        positiveCnt = positiveCnt + twComment[2]

                    if twComment[0] == 2 and twComment[2]:
                        negativeCnt=negativeCnt+twComment[2]

                    if twComment[0] == 3 and twComment[2]:
                        neutralCnt = neutralCnt + twComment[2]

                    myarray[0] = country
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
            mylist.append(list(myarray.values()))

    
    # Report for Location wise happiness quotient
    elif persona.report_type.id == 3  and CommentObj:
        scale = "Date Period"
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        for single_date in newDateRange:
            for location in locationsList:
                myarray = {}
                positiveCnt = 0
                negativeCnt = 0
                neutralCnt = 0
                cultureName=''
                for twComment in CommentObj:
                    if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d"):
                        if location == twComment[3]:
                            if twComment[0] == 1 and twComment[4]:
                                positiveCnt = positiveCnt + twComment[4]

                            if twComment[0] == 2 and twComment[4]:
                                negativeCnt = negativeCnt + twComment[4]

                            if twComment[0] == 3 and twComment[4]:
                                neutralCnt = neutralCnt + twComment[4]
                            cultureName=twComment[1]
                total = positiveCnt + negativeCnt + neutralCnt
                if total > 0:
                    myarray[0] = single_date.strftime("%b %d, %Y")
                    myarray[1] = positiveCnt
                    myarray[2] = negativeCnt
                    myarray[3] = neutralCnt
                    myarray[4] = total
                    myarray[5] = single_date.strftime("%A")
                    myarray[6] = location
                    myarray[7] = cultureName
                    mylist.append(list(myarray.values()))

        dataRow = []
        
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[5]
                dataDictRow["location"] = val[6]
                dataDictRow["culture"] = val[7]
                happy_comments = 0
                negative_comments = 0
                neutral_comments = 0
                if val[4] !=0:
                    happy_comments = val[1] / val[4] * 100
                    negative_comments = val[2] / val[4] * 100
                    neutral_comments = val[3] / val[4] * 100
                dataDictRow["happy_comments"] = '{0:.2f}'.format(happy_comments)
                dataDictRow["negative_comments"] = '{0:.2f}'.format(negative_comments)
                dataDictRow["neutral_comments"] = '{0:.2f}'.format(neutral_comments)
                dataRow.append(dataDictRow)


    # Report for Location wise languages comment counts
    elif persona.report_type.id == 4 or persona.report_type.id == 5 and CommentObj:
        scale = ""
        locations = []
        for twComment in CommentObj:
            locations.append(twComment[3])
        locationsList = list(set(locations))

        languages=[]
        for twComment in CommentObj:
            languages.append(twComment[0])
        languagesList = list(set(languages))

        mylist = []
        for single_date in newDateRange:
            for location in locationsList:
                for language in languagesList:
                    myarray = {}
                    commentCnt = 0
                    for twComment in CommentObj:
                        if twComment[2].strftime("%Y-%m-%d") == single_date.strftime("%Y-%m-%d") :
                            if location == twComment[3] and language == twComment[0]:
                                if twComment[4]:
                                    commentCnt = commentCnt + twComment[4]
                                    myarray[0] = single_date.strftime("%b %d, %Y")
                                    myarray[2] = single_date.strftime("%A")
                                    myarray[3] = twComment[3]
                                    myarray[4] = twComment[1]
                                    myarray[5] = twComment[0]
                                    myarray[1] = commentCnt

                    if myarray:
                        mylist.append(list(myarray.values()))


        dataRow = []
        if mylist:
            for val in mylist:
                dataDictRow = {}
                dataDictRow["date"] = val[0]
                dataDictRow["weekday"] = val[2]
                dataDictRow["location"] = val[3]
                dataDictRow["culture"] = val[4]
                dataDictRow["language"] = val[5]
                dataDictRow["comments_count"] = val[1]
                dataRow.append(dataDictRow)

    return dataRow, mylist, scale, CommentObj
    
def getCannedResponse(request, canned_response, account):
    dataDictRow = {}
    try:
        dataDictRow["id"] = canned_response[0]['id']
        dataDictRow["social_accounts_id"] = account['id']
        if account['provider'] == 'facebook':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
            fb_pages = fb_is_page_management.objects.filter(fb_account=account['id'])
            for page in fb_pages:
                dataDictRow['page_name'] = page.page_name

        if account['provider'] == 'twitter':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
        if account['provider'] == 'instagram':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['username']
        dataDictRow["positive_response_text"] = canned_response[0]['positive_response_text']
        dataDictRow["negative_response_text"] = canned_response[0]['negative_response_text']
        dataDictRow["neutral_response_text"] = canned_response[0]['neutral_response_text']
        dataDictRow["created_on"] = canned_response[0]['created_on']
        dataDictRow["source"] = account['provider']

    except Exception as e:
        print("9999999999999999999999999999999999999")
        print(e)
        print(canned_response.id)
        dataDictRow["id"] = canned_response.id
        dataDictRow["social_accounts_id"] = account['id']
        if account['provider'] == 'facebook':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['name'].capitalize() 
            fb_pages = fb_is_page_management.objects.filter(fb_account=account['id'])
            for page in fb_pages:
                dataDictRow['page_name'] = page.page_name

        if account['provider'] == 'twitter':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['access_token']['screen_name'].capitalize()
        if account['provider'] == 'instagram':
            dataDictRow['social_accounts_text'] = account['provider'].capitalize() + "-" + account['extra_data']['username']
        dataDictRow["positive_response_text"] = canned_response.positive_response_text
        dataDictRow["negative_response_text"] = canned_response.negative_response_text
        dataDictRow["neutral_response_text"] = canned_response.neutral_response_text
        dataDictRow["created_on"] = canned_response.created_on
        dataDictRow["source"] = account['provider']


    return dataDictRow