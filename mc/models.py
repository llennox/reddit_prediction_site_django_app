from __future__ import unicode_literals
from django.db import models
import re, uuid

class TheEmails(models.Model):
    emails = models.CharField(max_length=255, default="n/a")

class UserList(models.Model):
    username = models.CharField(max_length=255)
    subreddits = models.TextField()
    listuuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    label = models.CharField(max_length=255, null=True)
