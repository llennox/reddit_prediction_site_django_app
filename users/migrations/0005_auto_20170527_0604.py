# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-27 06:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170524_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profil',
            old_name='dispensary',
            new_name='verified_dispensary',
        ),
        migrations.RenameField(
            model_name='profil',
            old_name='distributer',
            new_name='verified_distributer',
        ),
    ]