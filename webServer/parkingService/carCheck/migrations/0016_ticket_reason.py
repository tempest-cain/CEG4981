# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-10 00:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0015_parkinglot_uncertain_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='reason',
            field=models.CharField(default='no pass', max_length=1000),
            preserve_default=False,
        ),
    ]
