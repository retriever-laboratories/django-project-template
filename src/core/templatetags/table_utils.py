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
