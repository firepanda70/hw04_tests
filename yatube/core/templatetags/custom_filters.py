from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
@stringfilter
def maketitle(text):
    if len(text) > 30:
        return text[:30] + '...'
    return text
