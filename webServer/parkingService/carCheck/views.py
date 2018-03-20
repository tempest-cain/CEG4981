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
from PIL import Image
from .models import *
# import numpy as np
import datetime
# import base64
import requests
# import time
import json
from .models import *

DEFAULT_FINE = 20


# Create your views here.
def index(request):
    return render(request, "index.html")

@csrf_exempt
def check(request):
    URL = "https://api.openalpr.com/v2/recognize"
    print("got here!")
    print(request.FILES)
    for image in request.FILES:
        PARAMS = {
                'secret_key':"sk_fd494c5574d66d4278ce39fe",
                'country':"us",
                'recognize vehicle':1,
                }
        files = {'image': request.FILES[image]}
        r = requests.post(url = URL, files=files, params = PARAMS)
        for car in  request.content.results:
            plateNum = request.content.results[car].plates
            certainty = request.content.results[car].confidence
            region = request.content.results[car].region
            if car.objects.get(licence_plate=plateNum) and certainty >.8:
                checkCar = car.objects.get(licence_plate=plateNum)
                if not checkcar.parking_pass or parking_pass.objects.get(pk=checkcar.parking_pass) <= datetime.datetime.now():
                    image.objects.create(ticketed_car=checkCar, fine_amount=DEFAULT_FINE, photo=request.FILES[image])
        return HttpResponse('{"123":123}')
    return JsonResponse({"Error": "No image file"})

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

def ticketView(request):
    data = {}
    data['tickets']= ticket.objects.all().order_by('-id')
    data['cars']= car.objects.all()
    return render(request, "tickets.html", context=data)


def photoview(request, pk = None):
    # image_data = open(image.objects.get(pk=pk).photo, "rb").read()
    return HttpResponse(image.objects.get(pk=pk).photo, content_type="image/png")
