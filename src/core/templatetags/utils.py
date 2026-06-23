from django import template
from django.utils.text import capfirst

register = template.Library()

PAGE_PARAMS = {"page", "o", "page_size"}


@register.simple_tag
def group_params(request):
    filter_params = []
    page_params = []

    for name, values in request.GET.lists():
        if name in PAGE_PARAMS:
            page_params.append((name, values))
            continue

        filter_params.append((name, values))

    return {
        "filters": filter_params,
        "page": page_params,
    }


@register.simple_tag
def clear_filters_url(request):
    applied_filters = group_params(request)["filters"]
    if not applied_filters:
        return None

    params = request.GET.copy()
    for field, _ in applied_filters:
        del params[field]

    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path


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
    for order_field in request.GET.getlist("o"):
        if order_field == field_name:
            return "asc"
        if order_field == f"-{field_name}":
            return "desc"
    return None


@register.simple_tag
def sort_url(request, field_name, direction):
    order_field = field_name if direction == "asc" else f"-{field_name}"
    current_order = request.GET.getlist("o")

    already_selected = order_field in current_order
    new_order = [entry for entry in current_order if entry.lstrip("-") != field_name]

    if not already_selected:
        new_order.append(order_field)

    params = request.GET.copy()
    params.setlist("o", new_order)

    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path


@register.simple_tag
def pagination_url(request, **changes):
    query_params = request.GET.copy()

    for name, value in changes.items():
        if value is None:
            query_params.pop(name, None)
            continue

        query_params[name] = value

    query_string = query_params.urlencode()
    return f"{request.path}?{query_string}" if query_string else request.path


@register.simple_tag
def remove_filter_url(request, key, value):
    params = request.GET.copy()
    params.setlist(key, [item for item in params.getlist(key) if item != value])

    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path
