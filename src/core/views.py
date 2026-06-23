from types import SimpleNamespace

from django.core.paginator import Paginator
from django.shortcuts import render

context = {
    "model": "User",
    "table": {
        "columns": [
            {
                "field": "id",
                "sortable": True,
                "partial": "partials/link.html",
                "class": "link-primary",
            },
            {
                "field": "name",
                "sortable": True,
            },
            {
                "field": "email",
                "sortable": True,
            },
            {
                "field": "role",
                "sortable": True,
            },
            {
                "field": "status",
                "sortable": False,
            },
        ],
        "actions": {
            "top_right": "partials/download_button.html",
            "bottom_right": "partials/add_button.html",
        },
    },
    "page_size_options": [
        {"size": 10, "url": "?page_size=10"},
        {"size": 50, "url": "?page_size=50"},
        {"size": 100, "url": "?page_size=100"},
    ],
    "object_list": [
        SimpleNamespace(
            id="01",
            name="Ada Lovelace",
            email="ada@example.com",
            role="Admin",
            status="Active",
        ),
        SimpleNamespace(
            id="02",
            name="Alan Turing",
            email="alan@example.com",
            role="Editor",
            status="Active",
        ),
        SimpleNamespace(
            id="03",
            name="Grace Hopper",
            email="grace@example.com",
            role="Editor",
            status="Invited",
        ),
    ],
    "filters": [ 
        {
            "field": "name",
            "filter_input_type": "text",
        },
        {
            "field": "role",
            "filter_input_type": "select",
            "options": [
                {"value": "admin", "label": "Admin"},
                {"value": "editor", "label": "Editor"},
                {"value": "viewer", "label": "Viewer"},
            ],
        },
        {
            "field": "status",
            "filter_input_type": "select",
            "options": [
                {"value": "active", "label": "Active"},
                {"value": "invited", "label": "Invited"},
                {"value": "disabled", "label": "Disabled"},
            ],
        },
    ],
}
paginator = Paginator(context["object_list"], 2)
context["page_obj"] = paginator.get_page(1)


def table(request):
    if request.htmx:
        return render(request, "table/partials/table.html", context)
    return render(request, "table/index.html", context)
