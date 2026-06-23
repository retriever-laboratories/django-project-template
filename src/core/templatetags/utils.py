from django import template

register = template.Library()


@register.filter(name="getattr")
def get_field(obj, field_name):
    return getattr(obj, field_name, "")


@register.simple_tag
def sort_direction(request, field_name):
    for token in request.GET.getlist("o"):
        if token == field_name:
            return "asc"
        if token == f"-{field_name}":
            return "desc"
    return None
