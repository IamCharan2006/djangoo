from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    # Now we have 4 steps, so each step is 25%
    return float(value) * float(arg) 