from django.db import models
from Customer.models import Customer
from Order.models import Order
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,related_name='customer_payment')
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,related_name='order_payment')
    payment_method = models.CharField(max_length=100)
    payment_status = models.BooleanField(default=False)
    total_amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_method