# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-08 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0009_remove_ticket_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='photo',
            field=models.ImageField(null=True, upload_to='./'),
        ),
    ]
