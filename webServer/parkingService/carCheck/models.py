# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class parking_pass(models.Model):
    pass_number = models.IntegerField(unique=True)
    expiration = models.DateField()
    owner = models.CharField(max_length=300) #would be student ID in real applicatoin

class car(models.Model):
    model = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 100)
    licence_plate = models.CharField(max_length=12, unique=True)
    color = models.CharField(max_length = 30)
    parking_pass = models.ForeignKey(parking_pass, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.licence_plate)

class ticket(models.Model):
    ticketed_car = models.ForeignKey(car)
    fine_amount = models.DecimalField(decimal_places=2, max_digits=10)
    photo = models.ImageField(upload_to='./', null = True)
    date=models.DateField(auto_now=True)

class parkingLot(models.Model):
    spots_scanned = models.IntegerField()
    spots_empty = models.IntegerField()

class uncertain_photos(models.Model):
    ticketed_car = models.CharField(max_length=10)
    fine_amount = models.DecimalField(decimal_places=2, max_digits=10)
    photo = models.ImageField(upload_to='./', null = True)
    action = models.CharField(max_length=1000)
    message = models.CharField(max_length = 1000)
    date=models.DateField(auto_now=True)
