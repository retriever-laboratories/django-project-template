from django import template

register = template.Library()


@register.filter
def getlist(querydict, key):
    return querydict.getlist(key)


@register.filter
def verbose_name(model, field_name):
    return model._meta.get_field(field_name).verbose_name


@register.filter
def list_add(values, item):
    return [*values, item] if item not in values else list(values)

@register.filter
def list_remove(values, item):
    return [v for v in values if v != item]


@register.filter
def as_dict(value, key):
    return {key: value}
