from django.db import models
from social_django.models import UserSocialAuth
from django.conf import settings
from authentication.models import User
from nationality.models import nationality_prediction
from nationality.models import usa_cities_master

class sentimentMaster(models.Model):
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.sentiment)

# Cutomer Profile Management
class customer_management(models.Model):
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_logo = models.ImageField(upload_to='company/', default='media/no-img.png')
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    mobile_no = models.PositiveIntegerField(null=True, blank=True)
    business_info = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Social Media Profiles'
        verbose_name_plural = 'Profiles'

    # def __str__(self):
    #     return self.company_name


# FB and IS Management
class fb_is_page_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    page_name = models.CharField(max_length=255, null=False, blank=False)
    user_access_token = models.CharField(max_length=255, null=False, blank=False)
    app_access_token = models.CharField(max_length=255, null=False, blank=False)
    page_access_token = models.CharField(max_length=255, null=False, blank=False)
    client_token = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    fb_account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True)
    page_id = models.CharField(max_length=255, null=True, blank=True)
    ig_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'FB IS Management Details'
        verbose_name_plural = 'FB IS Management Details'

    def __str__(self):
        return self.page_name

class removed_fb_page_details(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    page_name = models.CharField(max_length=255, null=False, blank=False)
    user_access_token = models.CharField(max_length=255, null=False, blank=False)
    app_access_token = models.CharField(max_length=255, null=False, blank=False)
    page_access_token = models.CharField(max_length=255, null=False, blank=False)
    fb_account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True)
    page_id = models.CharField(max_length=255, null=True, blank=True)

# Cutomer Canned Response Management
class canned_response_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    social_accounts = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True)
    positive_response_text = models.TextField(null=True, blank=True)
    neutral_response_text = models.TextField(null=True, blank=True)
    negative_response_text = models.TextField(null=True, blank=True)
    fb_page = models.ForeignKey(fb_is_page_management, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Canned Response Details'
        verbose_name_plural = 'Canned Responses'

    def __str__(self):
        return str(self.id)



class ReportParameter(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class ReportTypeMaster(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    parameters = models.ManyToManyField(ReportParameter)

    def __str__(self):
        return self.name

class customer_chiptiles(models.Model):
    customer_ref = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    chip_title = models.CharField(max_length=200, null=True)
    capture_facebook = models.BooleanField(default=False)
    capture_twitter = models.BooleanField(default=False)
    capture_instagram = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.ForeignKey(ReportTypeMaster, on_delete=models.CASCADE, null=True)
    date_duration_from = models.DateField(null=True, blank=True)
    date_duration_to = models.DateField(null=True, blank=True)
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    culture = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.chip_title

class fb_post_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=True, blank=True)
    fb_post_id = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    raw_response = models.TextField(null=False, blank=True)
    fb_account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE)
    fb_page = models.ForeignKey(fb_is_page_management, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.message)

class fb_comment_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    fb_post_ref = models.ForeignKey(fb_post_management, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=False, blank=False)
    fb_comment_id = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_replied = models.BooleanField(default=False)
    raw_response = models.TextField(null=False, blank=True)
    comment_language = models.CharField(max_length=255, null=True, blank=True)
    resposne_sent = models.TextField(null=True, blank=True)
    sentiment = models.ForeignKey(sentimentMaster, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    location_lat = models.CharField(max_length=255, null=True, blank=True)
    location_lon = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    nationality_percent = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)

    def __str__(self):
        return str(self.message)


class ig_post_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=True, blank=True)
    ig_post_id = models.CharField(max_length=255, null=False, blank=False)
    insta_account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    raw_response = models.TextField(null=False, blank=True)
    # media_type = models.CharField(max_length=255, null=True, blank=True)
    # media_url = models.CharField(max_length=255, null=True, blank=True)
    media_type = models.TextField(null=True, blank=True)
    media_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.message)

class ig_comment_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    ig_post_ref = models.ForeignKey(ig_post_management, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=False, blank=False)
    ig_comment_id = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_replied = models.BooleanField(default=False)
    raw_response = models.TextField(null=False, blank=True)
    comment_language = models.CharField(max_length=255, null=True, blank=True)
    commented_username = models.CharField(max_length=255, null=True, blank=True)
    sentiment = models.ForeignKey(sentimentMaster, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    location_lat = models.CharField(max_length=255, null=True, blank=True)
    location_lon = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    nationality_percent = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    comment_language = models.CharField(max_length=255, null=True, blank=True)
    resposne_sent = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.message)

class twitter_post_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    customer_chip_ref = models.ForeignKey(customer_chiptiles, on_delete=models.CASCADE, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=True, blank=True)
    tweet_id = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    raw_response = models.TextField(null=False, blank=True)
    twitter_account = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.message)



class twitter_comment_management(models.Model):
    customer_name = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    twitter_post_ref = models.ForeignKey(twitter_post_management, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=False)
    message = models.TextField(null=False, blank=False)
    tweet_reply_id = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_replied = models.BooleanField(default=False)
    raw_response = models.TextField(null=False, blank=True)
    resposne_sent = models.TextField(null=True, blank=True)
    sentiment = models.ForeignKey(sentimentMaster, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    location_lat = models.CharField(max_length=255, null=True, blank=True)
    location_lon = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    nationality_percent = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    comment_language = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)


################ persona tables  #################
class persona_location(models.Model):
    location = models.CharField(max_length=255, null=True, blank=True)


class customer_persona(models.Model):
    chip_title = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_ref = models.ForeignKey(customer_management, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportTypeMaster, on_delete=models.CASCADE, null=True)
    date_duration_from = models.DateField(null=True, blank=True)
    date_duration_to = models.DateField(null=True, blank=True)
    social_auth_id = models.ManyToManyField(UserSocialAuth)
    culture_id = models.ManyToManyField(nationality_prediction)
    loaction_id = models.ManyToManyField(persona_location)
    sentiment_id = models.ManyToManyField(sentimentMaster)

