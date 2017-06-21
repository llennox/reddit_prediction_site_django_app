from django.db import models
from django.contrib.auth.models import User
import re, uuid


class Profil(models.Model):
    user = models.OneToOneField(User, related_name='profile') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    verified_dispensary = models.CharField(max_length=2, null=True)
    verified_distributer = models.CharField(max_length=2, null=True)
    grower = models.BooleanField(default=False)
    medical = models.CharField(max_length=2, null=True)
    