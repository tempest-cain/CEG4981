# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-20 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0012_auto_20180320_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='parking_pass',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='carCheck.parking_pass'),
        ),
    ]
