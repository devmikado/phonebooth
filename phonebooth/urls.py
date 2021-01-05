"""phonebooth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from . import settings
from django.conf.urls.static import static
from customer_dashboard.urls import urlpatterns as dashboard_urls
from nationality.urls import urlpatterns as nationality_urls
from django.views.generic import RedirectView 
from b2b.urls import urlpatterns as b2b_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("authentication.urls")),  # add this
    url(r'^nationality/', include((nationality_urls, 'nationality'), namespace='nationality')),
    url(r'^customer/', include((dashboard_urls, 'customer'), namespace='customer')),
    url(r'^b2b/', include((b2b_urls, 'b2b'), namespace='b2b')),

    # social
    # url(r'^accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace="social")),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/media/booth.png')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)