from django.db import models

# Create your models here.
from django.db.models.functions import Lower

class hashtag_collections(models.Model):
    hashtag = models.CharField(max_length=255, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hashtag Collection'
        verbose_name_plural = 'Hashtag Collections'

    def save(self, *args, **kwargs):
        self.hashtag = self.hashtag.lower()
        return super(hashtag_collections, self).save(*args, **kwargs)

    def __str__(self):
        return self.hashtag



class usa_states_master(models.Model):
    state_code = models.CharField(max_length=2, blank=True, null=True)
    state_name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.state_code


class usa_cities_master(models.Model):
    usa_state = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=255, blank=True, null=True)
    county_name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)


class wordcloud_stopwords(models.Model):
    stop_word = models.CharField(max_length=255, blank=True, null=True)


class data_collection_logging(models.Model):
    searched_text = models.CharField(max_length=255, null=True, blank=True)
    request = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Twitter Data'
        verbose_name_plural = 'Twitter Data Collections'

    def save(self, *args, **kwargs):
        self.searched_text = self.searched_text.lower()
        return super(data_collection_logging, self).save(*args, **kwargs)

    def data_collection_requested_data():
        return data_collection_logging.objects.filter(is_locked=False,is_processed=False).all()

    def data_collection_locked_data():
        return data_collection_logging.objects.filter(is_locked=True,is_processed=False).all()


class tweet_basic_info(models.Model):
    tweet_id = models.BigIntegerField()
    tweet_text = models.TextField(null=True, blank=True)
    tweet_source = models.TextField(null=True, blank=True)
    is_tweet_truncated = models.BooleanField(default=False)
    tweet_geo = models.CharField(max_length=255, null=True, blank=True)
    tweet_coordinates = models.CharField(max_length=255, null=True, blank=True)
    tweet_contributors = models.CharField(max_length=255, null=True, blank=True)
    tweet_lang = models.CharField(max_length=15, null=True, blank=True)
    tweet_created_datetime = models.DateField(auto_now=False)
    is_pre_processed = models.BooleanField(default=False)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    data_collection_log = models.ForeignKey(data_collection_logging, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Tweet Basic Info'
        verbose_name_plural = 'Tweets Info'



class tweet_place_info(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    place_id = models.CharField(max_length=255, blank=True, null=True)
    place_type = models.CharField(max_length=255, blank=True, null=True)
    place_name = models.CharField(max_length=255, blank=True, null=True)
    place_full_name = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=65, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Place Info'
        verbose_name_plural = 'Collected Tweets Places'

   
class tweet_entities_hashtags(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    twit_hashtags = models.TextField(blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Hashtags'
        verbose_name_plural = 'Collected Tweets Hashtags'


class tweet_entities_symbols(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    symbols = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Symbols'
        verbose_name_plural = 'Collected Tweets Symbols'


class tweet_entities_user_mentions(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    user_mentions = models.TextField(blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Entities'
        verbose_name_plural = 'Collected Tweets Entities'


class tweet_entities_user_urls(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    urls = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Urls'
        verbose_name_plural = 'Collected Tweets URLS'


class tweet_metadata(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    iso_language_code = models.CharField(max_length=11, blank=True, null=True)
    result_type = models.CharField(max_length=50, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Metadata'
        verbose_name_plural = 'Collected Tweets Metadata'


class tweet_user_data(models.Model):
    tweet_basic_info_ref = models.ForeignKey(tweet_basic_info, on_delete=models.CASCADE)
    tweet_user_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    screen_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    is_protected = models.BooleanField(default=False)
    profile_created_at = models.DateTimeField(blank=True, null=True)
    utc_offset = models.CharField(max_length=15, blank=True, null=True)
    time_zone = models.CharField(max_length=64, blank=True, null=True)
    geo_enabled = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    lang = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Userdata'
        verbose_name_plural = 'Collected Tweets Userdata'


class forebears_logging(models.Model):
    tweet_user_data_ref = models.ForeignKey(tweet_user_data, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    request_text = models.TextField(blank=True, null=True)
    response_text = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Forebears Data'
        verbose_name_plural = 'Forebears Data Logging'


class nationality_prediction(models.Model):
    tweet_user_data_ref = models.ForeignKey(tweet_user_data, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    jurisdiction = models.CharField(max_length=255, blank=True, null=True)
    percent = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    sanitisedForename = models.CharField(max_length=255, blank=True, null=True)
    sanitisedSurname = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nationality Predicted User'
        verbose_name_plural = 'Nationality Predicted User'


class nationality_user_data_preprocess(models.Model):
    tweet_user_data_ref = models.ForeignKey(tweet_user_data, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    lang = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ethinicity Data Prepration'
        verbose_name_plural = 'Ethinicity Prepration List'


class tweet_analytics_processed_data(models.Model):
    tweet_user_id = models.BigIntegerField(blank=True, null=True)
    tweet_username = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_location = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_description = models.TextField(blank=True, null=True)
    tweet_user_profile_created_at = models.DateTimeField(blank=True, null=True)
    tweet_user_first_name = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_last_name = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_nationality_predicted = models.BooleanField(default=False)
    tweet_user_jurisdiction = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_percent = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    tweet_id = models.BigIntegerField()
    tweet_text = models.TextField(null=True, blank=True)
    tweet_lang = models.CharField(max_length=15, null=True, blank=True)
    tweet_created_datetime = models.DateField(auto_now=False)
    tweet_sentiment = models.CharField(max_length=255, blank=True, null=True)
    state_code = models.ForeignKey(usa_states_master, on_delete=models.CASCADE)
    city_code = models.ForeignKey(usa_cities_master, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(hashtag_collections, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tweet Preprocess Data'
        verbose_name_plural = 'Tweet Preprocess Data'


class chiptiles(models.Model):
    chip_title = models.CharField(max_length=200, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    nationalities = models.TextField(null=True)
    locations = models.TextField(null=True)
    hashtags = models.TextField(null=True)

