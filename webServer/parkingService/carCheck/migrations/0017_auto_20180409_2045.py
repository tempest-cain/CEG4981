# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-10 00:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carCheck', '0016_ticket_reason'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='parkingLot',
            new_name='parking_lot',
        ),
    ]
