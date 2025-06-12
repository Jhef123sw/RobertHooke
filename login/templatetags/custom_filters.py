# login/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, delimiter=" "):
    return value.split(delimiter)