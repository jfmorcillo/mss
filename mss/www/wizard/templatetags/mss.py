from django import template

register = template.Library()

@register.filter
def firstline(string):
    return string.split("\n")[0]
