from django import template
import datetime

register = template.Library()


@register.filter
def subtract(value, arg):
    dt = value - arg
    return str(dt).split(".")[0]
