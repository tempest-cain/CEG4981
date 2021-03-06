# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.files.storage import FileSystemStorage, default_storage
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.template import Context, loader
from django.conf.urls.static import static
from django.core.files import File
from django.utils import timezone
from django.conf import settings
from detect_cars import predict
from PIL import Image, ExifTags
from carCheck .forms import *
from .models import *
import datetime, os
import requests
import views
import json
DEFAULT_FINE = 20
NUM_SLOTS_SCANNED = 0
DEFAULT_LOT = 1

OPEN_ALPR_URL = "https://api.openalpr.com/v2/recognize"
OPEN_ALPR_PARAMS = {
        'secret_key':"sk_fd494c5574d66d4278ce39fe",
        'country':"us",
        'recognize_vehicle':1,
        }

def index(request):
    return render(request, "index.html")

def uncertainView(request):
    data = {}
    data['tickets']= uncertain_photos.objects.filter(processed = False).order_by('-id')
    return render(request, "uncertain.html", context=data)

def uncertainRequest(request, pk = None):
    result = 'failed'

    if len(uncertain_photos.objects.filter(pk=pk)) and not int(request.POST.get('delete')):
        uncertain = uncertain_photos.objects.get(pk=pk)
        if 0 == len(car.objects.filter(licence_plate=request.POST.get('plate'))):
            car.objects.create(licence_plate=request.POST.get('plate'))
        processed.objects.create(car = car.objects.get(licence_plate=request.POST.get('plate')), fine_amount = request.POST.get('fine') or DEFAULT_FINE, photo = uncertain.photo, fined=True)
        uncertain.processed = True
        uncertain.save()
        result = "Ticketed!"
    elif uncertain_photos.objects.get(pk=pk) and request.POST.get('delete'):
        uncertain = uncertain_photos.objects.get(pk=pk)
        uncertain.ignored = True
        uncertain.processed = True
        uncertain.save()
        resulted = 'Deleted!'
    return JsonResponse({'update':result})

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

def determine_if_license_plate_is_valid(openalpr_cars, request, image_path):
    carResults_certain = []
    carResults_not_certain = []
    if len(openalpr_cars['results']) == 0:
        carResults_not_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "No license plate detected"})
        return JsonResponse({"carResults_certain": carResults_certain, "carResults_not_certain" : carResults_not_certain })
    for carIndex in range(0, len(openalpr_cars['results'])):
        checkCar = openalpr_cars['results'][carIndex]
        plateNum = checkCar['plate']
        certainty = checkCar['confidence']
        region = checkCar['region']


        if (certainty <= 0.79 and len(carResults_certain) <= 0):
            # Add to uncertain and update view for review_needed
            # TODO (for JOHN): Update for review_needed
            # todo: REPLACE NOPASS WITH ACTION (JOHN)
            # File(open('path_to_pic/image.png', 'r')
            carResults_not_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "No license plate detected with certainty greater than 80%", "plateNum" : plateNum, "action" : action})

        if certainty > 0.8:
            #checkCar = car.objects.filter(licence_plate=plateNum)[0].parking_pass
            action = 'valid'
            vehicle_model = checkCar['vehicle']['body_type'][0]['name']+ ' ' + checkCar['vehicle']['year'][0]['name']
            vehicle_make = checkCar['vehicle']['make'][0]['name']
            vehicle_color = checkCar['vehicle']['color'][0]['name']

            # If car object is not in database:
            if not car.objects.filter(licence_plate=plateNum):
                # Create car object in database
                car.objects.create(model=vehicle_model, brand=vehicle_make, licence_plate=plateNum, color=vehicle_color)
                # Generate ticket because license plate is not in database
                processed.objects.create(car=car.objects.filter(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES['file'], fined=True)

                action = 'generate_ticket_because_license_plate_is_not_in_db'

                carResults_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "license plate detected with certainty greater than 80%", "plateNum" : plateNum, "action" : action})

            elif not (car.objects.filter(licence_plate=plateNum)[0].parking_pass):

                # Generate ticket because license plate is not under a parking pass
                processed.objects.create(car=car.objects.get(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES['file'], fined=True)

                action='generate_ticket_because_license_plate_is_not_registered_under_a_parking_pass'

                carResults_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "license plate detected with certainty greater than 80%", "plateNum" : plateNum, "action" : action})
            elif (car.objects.filter(licence_plate=plateNum)[0].parking_pass).expiration < datetime.datetime.now().date():
                # Generate ticket because license plate is under an expired pass
                processed.objects.create(car=car.objects.get(licence_plate=plateNum), fine_amount=DEFAULT_FINE, photo=request.FILES['file'], fined=True)

                action='generate_ticket_because_license_plate_is_registered_under_an_expired_parking_pass'

                carResults_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "license plate detected with certainty greater than 80%", "plateNum" : plateNum, "action" : action})

        if action == "valid":
            # TODO (for JOHN): create new view called processed and update processed view
            carResults_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "license plate detected with certainty greater than 80%", "plateNum" : plateNum, "action" : action})
            processed.objects.create(car=car.objects.get(licence_plate=plateNum), fine_amount=0, photo=request.FILES['file'], fined=False)

        return JsonResponse({"carResults_certain":carResults_certain, "carResults_not_certain" : carResults_not_certain })

@csrf_exempt
def check(request):

    # Assume no carResults
    carResult = "no_car"

    # Store picture into media folder for access
    data = request.FILES['file']
    image_path = default_storage.save('detect_cars/'+request.FILES['file'].name, request.FILES['file'])
    tmp_file = os.path.join(settings.MEDIA_ROOT, image_path)
    # Use image classifier to figure out if there is a car in the image
    carResult = predict.checkCar(request.FILES['file'].name)
    parking_lot.objects.get(pk = DEFAULT_LOT).spots_scanned +=1
    # If there is a not a car in the image figure increase the empty slot counter:
    carResults_certain = []
    if carResult == "no_car":
        parking_lot.objects.get(pk = DEFAULT_LOT).spots_empty +=1
        tmp_file_object = File(open(tmp_file, "r"))
        carResults_certain.append({"image_path": os.path.join(settings.MEDIA_ROOT, image_path), "license_plate_message" : "no_car_in_image", "plateNum" : "N/A", "action" : "no_car_in_image"})
        #processed.objects.create(car=car.objects.get(licence_plate="N/A"), fine_amount=0, photo=request.FILES['file'], fined=False)
        processed.objects.create(car=car.objects.get(licence_plate="N/A"), fine_amount=0, photo= "../media/" +image_path, fined=False)
        return JsonResponse(carResults_certain[0])

    # If there is a car in the image figure out if it needs a ticket:
    if carResult == "car":
        fix_image_rotation(image_path)
        files = {'image':  open(os.path.join(settings.MEDIA_ROOT, image_path))}
        r = requests.post(url = OPEN_ALPR_URL, files=files, params = OPEN_ALPR_PARAMS)
        openalpr_cars = json.loads(r.content)
        json_result_response = determine_if_license_plate_is_valid(openalpr_cars, request, image_path)
    return json_result_response

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
    # todo: JOHN ADD HOW MANY SCANNED, PROCESSED SLOTS, AND CONF = EMPY/SCANNED
    lots = []
    for item in parking_lot.objects.all():
        lot = {}
        lot['lot_name'] = item.lot_name
        lot['spots_empty'] = item.spots_empty
        lot['spots_scanned'] = item.spots_scanned
        lot['confRatio'] = "{0:.2f}".format(float(item.spots_empty*100)/item.spots_scanned)
        lots.append(lot)
    return render(request, "parking.html", context={'lots':lots})

def ticketView(request):
    data = {}
    data['tickets']= processed.objects.filter(fined=True).filter(sent=False).order_by('-id')
    return render(request, "tickets.html", context=data)

def processedView(request):
    data = {}
    # TODO (for JOHN): create add reson to view
    data['tickets']= processed.objects.filter(fined=False).order_by('-id')
    return render(request, "processed.html", context=data)

def sentView(request):
    data = {}
    data['tickets']= processed.objects.filter(sent=True).order_by('-id')
    return render(request, "sent.html", context=data)

def photoview(request, pk = None):
    return HttpResponse(image.objects.get(pk=pk).photo, content_type="image/png")

def ticketRequest(request, pk = None):
    row = processed.objects.get(pk=pk)
    action = "nothing"
    if int(request.GET.get('ignore')):
        row.fined = False
        row.save()
        action ="ignored"
    elif int(request.GET.get('sent')):
        row.sent = True;
        row.save()
        action="sent"
    return JsonResponse({"response":action})
