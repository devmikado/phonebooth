from django.urls import path
from django.conf.urls import url
from .views import *


urlpatterns = [ 
    url(r'^data-collection/$', TwitterAPIDataConnection.twitter_data_collection), 
    
    url(r'^data-processing/$', TwitterDataProcessing.process_collected_twits), 
    
    url(r'^prepare-naltionality-data/$', TwitterDataProcessing.prepare_nationality_data), 
    # nationality_prediction_data_process
    url(r'^prepare-prediction-naltionality-data/$', TwitterDataProcessing.nationality_prediction_data_process),

    # TweeterDataPreprocess
    # prepareTweeterDataPreprocess 
    url(r'^twitter-data-process/$', TweeterDataPreprocess.prepareTweeterDataPreprocess), 
    # url(r'^dashboard/$', TwitterAPIDataConnection.phonebooth_dashboard),
    path('dashboard/', TwitterAPIDataConnection.phonebooth_dashboard, name="dashboard"),

    url(r'^get-locations-list/$', TwitterAPIDataConnection.getLocationsList),
    url(r'^get-hashtags-list/$', TwitterAPIDataConnection.getHashtagsList),
    url(r'^get-nationalities-list/$', TwitterAPIDataConnection.getNationalitiesList),
    url(r'^save-new-chip-details/$', TwitterAPIDataConnection.addnewchip),
]