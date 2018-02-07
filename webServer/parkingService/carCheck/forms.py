from django import forms
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.conf import settings    
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
# import datetime
# from django.utils import timezone
from .models import *

class UserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=20)

    def clean(self):
        data = self.cleaned_data
        user = authenticate(
        username=data['username'], password=data['password'])
        if user is None:
            raise forms.ValidationError('Username or password is Invalid')
        return data


class NewUserForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=254)

    def save(self):
        if self.is_valid:
            newUser = User(**self.cleaned_data)
            newUser.save()
            return newUser
