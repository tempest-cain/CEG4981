# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-12 20:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0026_auto_20180411_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='processed',
            name='sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='parking_pass',
            name='expiration',
            field=models.DateField(default=datetime.date(2018, 4, 12)),
        ),
    ]
