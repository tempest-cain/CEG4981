# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-07 21:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0005_auto_20180307_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='parking_pass',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='carCheck.parking_pass'),
            preserve_default=False,
        ),
    ]
