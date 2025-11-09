from django.db import models
from django.db import models
from home.models import Seller
from Customer.models import Customer
# Create your models here.

class Product(models.Model):
    model = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    seller=models.ForeignKey(Seller,on_delete=models.CASCADE,related_name='products',null=True)
    reciever=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='reciever',null=True)
    recieved = models.BooleanField(default=False)
    sold_date = models.DateTimeField(null=True, blank=True)
    sold = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    digital = models.BooleanField(default=False, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return f"Image for {self.product.name}"
