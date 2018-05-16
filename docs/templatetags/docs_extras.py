from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def fi_nbr(value, decimals=None):
    if decimals is not None:
        s = "{:0,.%df}" % decimals
    else:
        s = "{:0,.0f}"
    value = s.format(value).replace(',', ' ')
    return str(value).replace('.', ',')

@register.filter
def person(prs):
    return mark_safe("<strong>%s</strong><br>%s<br>%s" % (prs.name, prs.phone, prs.email))

@register.filter
def to_notes(notes):
    return mark_safe(notes.replace("\n", '<br>'))

@register.filter
def greek_talents(kg):
    return int(round(kg / 20.4))

@register.filter
def bib_capacity(capacity):
    ephahs = capacity / 1000000 / 22
    #if ephahs > 10:
    #    return "%d homers" % int(round(ephahs / 10))
    return "%d ephahs" % int(round(ephahs))
