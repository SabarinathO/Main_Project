from django import template
from Order.models import Order, OrderItem
register = template.Library()

@register.filter
def subtotal(price,quantity):
    return price*quantity

