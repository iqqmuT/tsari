from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def fi_nbr(value, decimals=None):
    if decimals is not None:
        s = "{:0.%df}" % decimals
        value = s.format(value)
    return str(value).replace('.', ',')

@register.filter
def person(prs):
    return mark_safe("<strong>%s</strong><br>%s<br>%s" % (prs.name, prs.phone, prs.email))

@register.filter
def to_notes(notes):
    return mark_safe(notes.replace("\n", '<br>'))
