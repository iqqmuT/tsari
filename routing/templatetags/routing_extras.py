from django import template

register = template.Library()

@register.filter
def route_class(value):
    if value == 'convention':
        return 'success'
    elif value == 'location':
        return 'info'
    return 'secondary'
