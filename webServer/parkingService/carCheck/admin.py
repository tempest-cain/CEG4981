# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(parking_pass)
admin.site.register(car)
admin.site.register(processed)
admin.site.register(parking_lot)
admin.site.register(uncertain_photos)
