from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    zip = models.CharField(max_length=50,null=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name