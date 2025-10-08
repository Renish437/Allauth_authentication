from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomProfiles(AbstractUser):
    phone = models.CharField(max_length=30,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_social = models.BooleanField(default=False)
    dob = models.DateField(null=True,blank=True)
    
    



