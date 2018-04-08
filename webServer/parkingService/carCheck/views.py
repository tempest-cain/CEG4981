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
#from django.views import View
import views
from carCheck .forms import *
# import tensorflow as tf
from PIL import Image
from .models import *
# import numpy as np
import datetime, os
# import base64
import requests
# import time
import json
from .models import *
from detect_cars import predict

from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ExifTags

EMPTY_SLOTS = 0
DEFAULT_FINE = 20

OPEN_ALPR_URL = "https://api.openalpr.com/v2/recognize"
OPEN_ALPR_PARAMS = {
        'secret_key':"sk_fd494c5574d66d4278ce39fe",
        'country':"us",
        'recognize_vehicle':1,
        }

# Create your views here.
def index(request):
    return render(request, "index.html")

@csrf_exempt
def checkbyjohn(request):
    URL = "https://api.openalpr.com/v2/recognize"
    for image in request.FILES:
        PARAMS = {
                'secret_key':"sk_fd494c5574d66d4278ce39fe",
                'country':"us",
                'recognize_vehicle':1,
                }
        files = {'image': request.FILES[image]}
        print type(files["image"])
        r = requests.post(url = URL, files=files, params = PARAMS)
        cars = json.loads(r.content)
        print cars
        for carIndex in  range(0, len(cars['results'])):
            checkCar = cars['results'][carIndex]
            plateNum = checkCar['plate']
            certainty = checkCar['confidence']
            region = checkCar['region']
            carResults = []
            if certainty >.8:
                # checkCar = car.objects.filter(licence_plate=plateNum)
                action = 'valid'
                if not car.objects.filter(licence_plate=plateNum):
                    car.objects.create(model =checkCar['vehicle']['body_type'][0]['name']+' '+checkCar['vehicle']['year'][0]['name'], brand=checkCar['vehicle']['make'][0]['name'], licence_plate=plateNum, color=checkCar['vehicle']['color'][0]['name'])
                    ticket.objects.create(ticketed_car=car.objects.filter(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])

                    action='ticket'
                elif not car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass) <= datetime.datetime.now():
                    # elif not parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum))[0].parking_pass <= datetime.datetime.now():
                    ticket.objects.create(ticketed_car=car.objects.get(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])
                    action='ticket'
                carResults.append([plateNum, action])


        return JsonResponse({"results":carResults})
    return JsonResponse({"Error": "No image file"})

def fix_image_rotation(image_path):
    try:
        image=Image.open(os.path.join(settings.MEDIA_ROOT, image_path))
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)
        image.save(os.path.join(settings.MEDIA_ROOT, image_path))
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

@csrf_exempt
def check(request):

    # Assume no carResults
    carResult = "no_car"

    print ("File", request.FILES['file'].name)
    #print ("Image", request.FILES[image])

    # Store picture into media folder for access
    data = request.FILES['file']
    image_path = default_storage.save('detect_cars/'+request.FILES['file'].name, request.FILES['file'])
    tmp_file = os.path.join(settings.MEDIA_ROOT, image_path)

    # print (settings.MEDIA_ROOT, image_path)
    # print ("curre_path", os.path.dirname(os.path.realpath(__file__)))
    # print os.path.join(settings.MEDIA_ROOT, image_path)

    # Use image classifier to figure out if there is a car in the image
    carResult = predict.checkCar(request.FILES['file'].name)
    # print carResult

    # TODO (for JOHN): Increase database counter for number of slots scanned

    # If there is a not a car in the image figure increase the empty slot counter:
    if carResult == "no_car":
        #EMPTY_SLOTS = EMPTY_SLOTS + 1
        # TODO (for JOHN): Increase database counter for empty slots
        return JsonResponse({"Car_result": "Empty parking slot"})

    # If there is a car in the image figure out if it needs a ticket:
    if carResult == "car":
        fix_image_rotation(image_path)
        files = {'image':  open(os.path.join(settings.MEDIA_ROOT, image_path))}
        print type(files["image"])
        r = requests.post(url = OPEN_ALPR_URL, files=files, params = OPEN_ALPR_PARAMS)
        openalpr_cars = json.loads(r.content)
        print openalpr_cars
        for carIndex in range(0, len(openalpr_cars['results'])):
            checkCar = cars['results'][carIndex]
            plateNum = checkCar['plate']
            certainty = checkCar['confidence']
            region = checkCar['region']
            carResults = []
            if certainty >0.8:
                # checkCar = car.objects.filter(licence_plate=plateNum)
                action = 'valid'
                if not car.objects.filter(licence_plate=plateNum):
                    car.objects.create(model =checkCar['vehicle']['body_type'][0]['name']+' '+checkCar['vehicle']['year'][0]['name'], brand=checkCar['vehicle']['make'][0]['name'], licence_plate=plateNum, color=checkCar['vehicle']['color'][0]['name'])
                    #ticket.objects.create(ticketed_car=car.objects.filter(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])

                    action='ticket_because_plate_not_in_db'
                elif not car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass) <= datetime.datetime.now():
                    # elif not parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum))[0].parking_pass <= datetime.datetime.now():
                    #ticket.objects.create(ticketed_car=car.objects.get(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])
                    action='ticket_because_expired_pass_or_no_pass_but_plate_in_db'
                carResults.append([plateNum, action])
            print action
            return JsonResponse({plateNum: action})

        return JsonResponse({"results":carResults})
    return JsonResponse({"Error": "No image file"})


@csrf_exempt
def checkbygoonmeetold(request):
    URL = "https://api.openalpr.com/v2/recognize"
    # Assume no carResults
    carResults = "no_car"
    files_with_cars = []
    for image in request.FILES:
        print ("File", request.FILES['file'].name)
        #x = request.FILES['file'].read()
        #exit()
        print ("Image", request.FILES[image])
        ### get the inmemory file


        data = request.FILES[image] # or self.files['image'] in your form
        path = default_storage.save('detect_cars/'+request.FILES['file'].name, request.FILES[image])
        print (settings.MEDIA_ROOT, path)
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)


        print ("curre_path", os.path.dirname(os.path.realpath(__file__)))


        carResults = predict.checkCar(request.FILES['file'].name)
        print carResults
        print os.path.join(settings.MEDIA_ROOT, path)

        if carResults == "car":
            try:
                image=Image.open(os.path.join(settings.MEDIA_ROOT, path))
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation]=='Orientation':
                        break
                exif=dict(image._getexif().items())

                if exif[orientation] == 3:
                    image=image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image=image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image=image.rotate(90, expand=True)
                image.save(os.path.join(settings.MEDIA_ROOT, path))
                image.close()

            except (AttributeError, KeyError, IndexError):
                # cases: image don't have getexif
                pass
            PARAMS = {
                    'secret_key':"sk_fd494c5574d66d4278ce39fe",
                    'country':"us",
                    'recognize_vehicle':1,
                    }
            files = {'image':  open(os.path.join(settings.MEDIA_ROOT, path))}
            print type(files["image"])
            r = requests.post(url = URL, files=files, params = PARAMS)
            cars = json.loads(r.content)
            print cars
            for carIndex in  range(0, len(cars['results'])):
                checkCar = cars['results'][carIndex]
                plateNum = checkCar['plate']
                certainty = checkCar['confidence']
                region = checkCar['region']
                carResults = []
                if certainty >.8:
                    # checkCar = car.objects.filter(licence_plate=plateNum)
                    action = 'valid'
                    if not car.objects.filter(licence_plate=plateNum):
                        car.objects.create(model =checkCar['vehicle']['body_type'][0]['name']+' '+checkCar['vehicle']['year'][0]['name'], brand=checkCar['vehicle']['make'][0]['name'], licence_plate=plateNum, color=checkCar['vehicle']['color'][0]['name'])
                        #ticket.objects.create(ticketed_car=car.objects.filter(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])

                        action='ticket_because_plate_not_in_db'
                    elif not car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass) <= datetime.datetime.now():
                        # elif not parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum)[0].parking_pass or parking_pass.objects.get(pk=car.objects.filter(licence_plate=plateNum))[0].parking_pass <= datetime.datetime.now():
                        #ticket.objects.create(ticketed_car=car.objects.get(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES[image])
                        action='ticket_because_expired_pass_or_no_pass_but_plate_in_db'
                    carResults.append([plateNum, action])
                print action
                return JsonResponse({plateNum: action})
        else:
            EMPTY_SLOTS = EMPTY_SLOTS + 1
        return JsonResponse({"results":carResults})
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

def simple_upload(request):
    print "OMG"
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'core/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'core/simple_upload.html')


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
