from django.urls import path
from django.conf.urls import url, include
from customer_dashboard.views import customerDetailView
from .views import *

urlpatterns = [ 
    # path('customer-dashboard/', customer_dashboard, name="customer-dashboard"),
    path('reports/', ReportView.reports, name="reports"),
    path('twitter-report/<str:type>/', ReportView.twitter_report, name="twitter-report"),
    path('fb-report/<str:type>/', ReportView.fb_report, name="fb-report"),
    path('insta-report/<str:type>/', ReportView.insta_report, name="insta-report"),
    path('put-reply-on-comment/', ReportView.putCommentReply, name="put-reply-on-comment"),
    path('custom-response/', CannedResponse.cannedResponseList, name="custom-response"),
    path('add-canned-response/', CannedResponse.addCannedReponse, name="add-canned-response"),
    path('edit-custom-response/<int:id>/', CannedResponse.editCannedReponse, name="edit-custom-response"),
    path('delete-canned-response/<int:pk>/', CannedResponse.deleteCannedResponse, name="delete-canned-response"),

    # persona url
    path('persona-list/', PersonaView.PersonaListView, name='persona-list'),
    path('add-customer-chip/', PersonaView.addCustomerNewChip, name='add-customer-chip'),
    path('edit-persona-data/', PersonaView.editPersonaData,name='edit-persona-data'),
    path('edit-persona-details/<str:id>/', PersonaView.editPersonaDetails,name='edit-persona-details'),
    path('add-new-persona/', PersonaView.addNewPersona, name='add-new-persona'),
    path('get_persona_report/<str:id>/', get_persona_report, name='get_persona_report'),
    path('persona-report/', PersonaView.PersonaReportView, name='persona-report'),
    path('delete-persona-details/<str:id>/', deletePersonaDetails, name='delete-persona-details'),

    path('get-report-type/', get_report_type, name='get-report-type'),
    path('get_report_title/<str:id>/', get_report_title, name='get-report-title'),
    path('get-all-report-type/', get_all_report_type, name='get-all-report-type'),
    path('get-paramters/<str:type>/', get_parameters, name='get-paramters'),
    path('get-sentiment/', get_sentiment, name="get-sentiment"),
    path('get-social-accounts/', getSocialAccounts, name="get-social-accounts"),
    path('get-locations-list/', getLocationsList, name='get-locations-list'),
    path('get-nationalities-list/', getNationalitiesList, name='get-nationalities-list'),



    path('get-report-details/<str:report_type>/', get_report_details, name='get-report-details'),
    path('get_parameters_details/<str:id>/', get_parameters_details, name='get-parameters-details'),
    path('get_edit_parameters_details/<str:id>/', get_edit_parameters_details, name='get-edit-parameters-details'),


    path('fb/', get_facebook_comment, name='fb'),


    



    
 ]