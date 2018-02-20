# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class parking_pass(models.Model):
    pass_number = models.IntegerField(unique=True)
    expiration = models.CharField(max_length=30)
    owner = models.CharField(max_length=300) #would be student ID in real applicatoin

class car(models.Model):
    model = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 100)
    licence_plate = models.CharField(max_length=12, unique=True)
    color = models.CharField(max_length = 30)
    parking_pass = models.ForeignKey(parking_pass)

class ticket(models.Model):
    car = models.ForeignKey(car)
    parking_pass = models.ForeignKey(parking_pass, blank=True)
    fine_amount = models.DecimalField(decimal_places=2, max_digits=10)
    photo = models.FileField()
