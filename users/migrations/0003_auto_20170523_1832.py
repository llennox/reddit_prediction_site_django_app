# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-23 18:32
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170523_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profil',
            name='id',
        ),
        migrations.AddField(
            model_name='profil',
            name='user_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
