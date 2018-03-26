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
    for image in request.FILES:
        PARAMS = {
                'secret_key':"sk_fd494c5574d66d4278ce39fe",
                'country':"us",
                'recognize_vehicle':1,
                }
        files = {'image': request.FILES[image]}
        r = requests.post(url = URL, files=files, params = PARAMS)
        cars = json.loads(r.content)
        for carIndex in  range(0, len(cars['results'])):
            checkCar = cars['results'][carIndex]
            print(checkCar)
            plateNum = checkCar['plate']
            certainty = checkCar['confidence']
            region = checkCar['region']
            carResults = []
            if certainty >.8:
                # checkCar = car.objects.filter(licence_plate=plateNum)
                action = 'valid'
                if not car.objects.filter(licence_plate=plateNum):


                    # last error message:
            #     response = wrapped_callback(request, *callback_args, **callback_kwargs)
            #   File "A:\Documents\Gitlab\drone\CEG4981\venv\lib\site-packages\django\views\decorators\csrf.py", line 58, in wrapped_view
            #     return view_func(*args, **kwargs)
            #   File "A:\Documents\Gitlab\drone\CEG4981\webServer\parkingService\carCheck\views.py", line 75, in check
            #     image.objects.create(ticketed_car=checkCar, fine_amount=DEFAULT_FINE, photo=requests.FILES[image])
            # AttributeError: 'unicode' object has no attribute 'objects'
            # [25/Mar/2018 17:48:43] "POST /check/ HTTP/1.1" 500 85775


                    newCar = car.objects.create(model =checkCar['vehicle']['body_type'][0]['name']+' '+checkCar['vehicle']['year'][0]['name'], brand=checkCar['vehicle']['make'][0]['name'], licence_plate=plateNum, color=checkCar['vehicle']['color'][0]['name'])
                    ticket.objects.create(ticketed_car=car.objects.filter(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=requests.FILES[image])

                    action='ticket'
                elif not car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass) <= datetime.datetime.now():
                    # elif not parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum))[0].parking_pass <= datetime.datetime.now():
                    image.objects.create(ticketed_car=checkCar, fine_amount=DEFAULT_FINE, photo=requests.FILES[image])
                    action='ticket'
                carResults.append([plateNum, action])


        return JsonResponse({"results":carResults1})
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
