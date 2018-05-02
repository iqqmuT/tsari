from django import template

register = template.Library()

@register.filter
def fi_nbr(value):
    return str(value).replace('.', ',')
