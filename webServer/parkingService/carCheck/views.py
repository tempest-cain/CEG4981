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
import numpy as np
import datetime
import base64
import time
import json


def index(request):
    return render(request, "index.html")

@csrf_exempt
def check(request):
    # fs = FileSystemStorage()
    # values = {}
    # for newImage in request.FILES:
    #     newImageObject = image.objects.create(photo = request.FILES[newImage])
    #     im = Image.open(request.FILES[newImage]).convert('RGB')
    #     im = im.resize((227, 227), Image.BILINEAR)
    #     img_tensor = [np.asarray(im, dtype=np.float32)]
    #     scores = sess.run(class_scores, {x_input: img_tensor, keep_prob: 1.}).tolist()
    #     filename = request.FILES[newImage].name
    #     newImageObject.positiveCertainty = scores[0][0]
    #     newImageObject.negativeCertainty = scores[0][1]
    #     newImageObject.certainty = max(min(((scores[0][0]-scores[0][1])/4),1),-1)
    #     newImageObject.save()
    #     print({"photo":newImageObject.photo, "positive":newImageObject.positiveCertainty, "negative":newImageObject.negativeCertainty})
    #     values[filename] = {"positive":newImageObject.positiveCertainty, "negative":newImageObject.negativeCertainty, "certainty":newImageObject.certainty}
    return JsonResponse(values)


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
            login(request, User.objects.get(username = request.POST.get('username')))
            return HttpResponseRedirect('/')
    return render(request, 'create.html', {'usernames': list(User.objects.all().values_list('username', flat=True))})
