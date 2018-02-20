# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
from django.template import Context, loader
# from .serializers import EventSerializer
from django.utils import timezone
from django.conf import settings
from django.views import View
from carCheck .forms import *
# import tensorflow as tf
# from PIL import Image
from .models import *
# import numpy as np
# import datetime
# import base64
# import time
import json

# Create your views here.
def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        userForm = UserForm(request.POST)
        if userForm.is_valid():
            data = userForm.cleaned_data
            user = authenticate(
                username=data['username'], password=data['password'])
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/')
        else:
            return render(request, "login.html", {'form': userForm})
    return render(request, 'login.html', {'form': UserForm()})


def createAccount(request):
    if request.method == "POST":
        user = NewUserForm(request.POST)
        if user.is_valid():
            loginUser = user.save()
            userLogin = authenticate(
                username=request.POST.get('username'), password=request.POST.get('password'))
            auth_login(request, User.objects.get(username = request.POST.get('username')))
            return HttpResponseRedirect('/')
    return render(request, 'create.html', {'usernames': list(User.objects.all().values_list('username', flat=True))})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def parking(request):
    return render(request, "parking.html")

def ticket(request):
    return render(request, "tickets.html")
