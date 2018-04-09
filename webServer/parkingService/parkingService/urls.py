"""parkingService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib import admin
# from django.urls import path
from django.views.static import serve
from carCheck.views import *
import settings

urlpatterns = [
    url(r'^$', index),
    url(r'^admin/', admin.site.urls),
    url(r'^login/', login),
    url(r'^logout/', logout_view),
    url(r'^createaccount/', createAccount),
    url(r'^parking/', parking),
    url(r'^ticket/', ticketView),
    url(r'^uncertain/(?P<pk>.*)$', uncertainRequest),
    url(r'^uncertain/', uncertainView),
    url(r'^check/', check, name="check"),
    url(r'^checkbyjohn/', checkbyjohn, name="checkbyjohn"),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # url(r'^control/', control),
]
