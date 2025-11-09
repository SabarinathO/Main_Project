from django import template
from django.utils.timezone import localtime, now
from datetime import timedelta

register = template.Library()

@register.filter
def is_yesterday(timestamp):
    """
    Check if the given timestamp is from yesterday.
    """
    timestamp = localtime(timestamp).date()
    return timestamp == (now().date() - timedelta(days=1))
