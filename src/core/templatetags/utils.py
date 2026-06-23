from django import template
from django.utils.text import capfirst

register = template.Library()


@register.filter(name="getattr")
def get_field(obj, field_name):
    return getattr(obj, field_name, "")


@register.filter
def getlist(querydict, key):
    return querydict.getlist(key)


@register.filter
def verbose_name(model, field_name):
    return capfirst(model._meta.get_field(field_name).verbose_name)


@register.simple_tag
def sort_direction(request, field_name):
    for token in request.GET.getlist("o"):
        if token == field_name:
            return "asc"
        if token == f"-{field_name}":
            return "desc"
    return None
