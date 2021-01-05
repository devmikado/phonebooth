from django.urls import path
from django.conf.urls import url, include
from customer_dashboard.views import customerDetailView
from nationality.views import TwitterAPIDataConnection
from .views import *
# from .tasks import get_all_tweets

urlpatterns = [
    # path('login/', login_view, name='login'),
    # path('register/', register_user, name="register"),
    path('customer-dashboard/', CustomerDashboard.customer_dashboard, name="customer-dashboard"),
    
    path('social-accounts/', SocialMediaPlatform.socialmdedia, name='social-accounts'),
    # path('twitter/', SocialMediaPlatform.twitter, name='twitter'),
    # url(r'^customer-dashboard/$', TwitterAPIDataConnection.customer_dashboard),
    path('customers-list/', customerListView.as_view(), name='customers-list'),
    path('customer-report/', customerReportView.as_view(), name='customer-report'),
    path('customers-details/<int:pk>/', customerDetailView.as_view(), name='customers-details'),
    # path('save-customer-chip-details/', TwitterAPIDataConnection.addCustomerNewChip,'save-customer-chip-details'),
    path('user-profile/<int:id>/', user_profile, name='user-profile'),

    path("insta-login/", connectInstagram, name="insta-login"),
    path("on-login/", on_login, name="on-login"),

    path("get-task/", get_tweets_for_user, name="get-task"),


    # ajax
    path('get-social-accounts/', get_social_account, name='get-social-accounts'),
    path('disconnect-social-accounts/<int:pk>/<str:platform>/', disconnect_social_account, name='disconnect-social-accounts'),

    path('social-auth/complete/instagram/', auth, name='auth'),
    path("insta-data/", getInstaFeeds, name='insta-data'),
    path('fb/', get_facebook_comment, name='fb'),

    path("change-status/<int:pk>/", changeStatus, name="change-status"),

    path("social/", socialAccount),

    path("download/", download),

    path("dashboard-reports/", dashboardReports, name="dahsboard-reports"),

    path("free-listening/", freeListening, name="free-listening"),

    path("get-countries/", getCountryName, name="get-countries"),
    # getCountryName
    path("get-cities/", getCityName, name="get-cities"),
    path("get-hashtags/", getHashtags, name="get-hashtags"),
    # getNationality
    path("get-nationality/", getNationality, name="get-nationality"),

    path("get-filters/", getFilterData, name='get-filter'),
]