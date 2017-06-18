from __future__ import unicode_literals
from django.db import models

class TheEmails(models.Model):
    emails = models.CharField(max_length=255, default="n/a")
