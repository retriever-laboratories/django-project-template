from django import template

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
def clear_filter_params(request):
    applied_filters = group_params(request)["filters"]
    if not applied_filters:
        return None

    params = request.GET.copy()
    for field, _ in applied_filters:
        del params[field]

    return params


@register.filter
def getlist(querydict, key):
    return querydict.getlist(key)


@register.filter
def verbose_name(model, field_name):
    return model._meta.get_field(field_name).verbose_name


@register.simple_tag
def sort_direction(request, field_name):
    for order_field in request.GET.getlist("o"):
        if order_field == field_name:
            return "asc"
        if order_field == f"-{field_name}":
            return "desc"
    return None


@register.simple_tag
def sort_params(request, field_name, direction):
    order_field = field_name if direction == "asc" else f"-{field_name}"
    current_order = request.GET.getlist("o")

    already_selected = order_field in current_order
    new_order = [entry for entry in current_order if entry.lstrip("-") != field_name]

    if not already_selected:
        new_order.append(order_field)

    params = request.GET.copy()
    params.setlist("o", new_order)

    return params


@register.simple_tag
def remove_filter_params(request, key, value):
    params = request.GET.copy()
    params.setlist(key, [item for item in params.getlist(key) if item != value])

    return params
