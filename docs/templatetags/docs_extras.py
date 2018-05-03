from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def fi_nbr(value):
    return str(value).replace('.', ',')

@register.filter
def person(prs):
    return mark_safe("<strong>%s</strong><br>%s<br>%s" % (prs.name, prs.phone, prs.email))
