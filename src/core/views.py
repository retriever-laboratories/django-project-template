from types import SimpleNamespace

from django.shortcuts import render


TABLE_SPEC = {
    "id": "users",
    "filters_base_url": "/table/?sort=name",
    "filters_applied": True,
    "filters": [
        {
            "accessor": "name",
            "label": "Name",
            "type": "text",
            "values": ["Ada"],
            "badges": [{"value": "Ada", "remove_url": "?role=admin&role=editor"}],
        },
        {
            "accessor": "email",
            "label": "Email",
            "type": "text",
            "values": [],
            "badges": [],
        },
        {
            "accessor": "role",
            "label": "Role",
            "type": "select",
            "options": [
                {"value": "admin", "label": "Admin"},
                {"value": "editor", "label": "Editor"},
                {"value": "viewer", "label": "Viewer"},
            ],
            "values": ["admin", "editor"],
            "badges": [
                {"value": "admin", "remove_url": "?name=Ada&role=editor"},
                {"value": "editor", "remove_url": "?name=Ada&role=admin"},
            ],
        },
        {
            "accessor": "status",
            "label": "Status",
            "type": "select",
            "options": [
                {"value": "active", "label": "Active"},
                {"value": "invited", "label": "Invited"},
                {"value": "disabled", "label": "Disabled"},
            ],
            "values": [],
            "badges": [],
        },
    ],
    "columns": [
        {
            "accessor": "id",
            "label": "Id",
            "sort": {
                "enabled": True,
                "direction": None,
                "asc_url": "/table/?name=Ada&role=admin&role=editor&sort=id",
                "desc_url": "/table/?name=Ada&role=admin&role=editor&sort=-id",
            },
        },
        {
            "accessor": "name",
            "label": "Name",
            "sort": {
                "enabled": True,
                "direction": "asc",
                "asc_url": "/table/?name=Ada&role=admin&role=editor",
                "desc_url": "/table/?name=Ada&role=admin&role=editor&sort=-name",
            },
        },
        {
            "accessor": "email",
            "label": "Email",
            "sort": {
                "enabled": True,
                "direction": None,
                "asc_url": "/table/?name=Ada&role=admin&role=editor&sort=email",
                "desc_url": "/table/?name=Ada&role=admin&role=editor&sort=-email",
            },
        },
        {
            "accessor": "role",
            "label": "Role",
            "sort": {
                "enabled": True,
                "direction": None,
                "asc_url": "/table/?name=Ada&role=admin&role=editor&sort=role",
                "desc_url": "/table/?name=Ada&role=admin&role=editor&sort=-role",
            },
        },
        {
            "accessor": "status",
            "label": "Status",
            "sort": {
                "enabled": False,
            },
        },
    ],
    "rows": [
        {
            "id": 1,
            "cells": [
                {
                    "accessor": "id",
                    "value": "01",
                    "render": "partials/link.html",
                    "class": "link-primary",
                    "props": {"href": "#"},
                },
                {"accessor": "name", "value": "Ada Lovelace", "class": "font-bold"},
                {"accessor": "email", "value": "ada@example.com"},
                {"accessor": "role", "value": "Admin"},
                {
                    "accessor": "status",
                    "value": "Active",
                    "render": "partials/badge.html",
                    "class": "badge-success",
                },
            ],
        },
        {
            "id": 2,
            "cells": [
                {
                    "accessor": "id",
                    "value": "02",
                    "render": "partials/link.html",
                    "class": "link-primary",
                    "props": {"href": "#"},
                },
                {"accessor": "name", "value": "Alan Turing", "class": "font-bold"},
                {"accessor": "email", "value": "alan@example.com"},
                {"accessor": "role", "value": "Editor"},
                {
                    "accessor": "status",
                    "value": "Active",
                    "render": "partials/badge.html",
                    "class": "badge-success",
                },
            ],
        },
        {
            "id": 3,
            "cells": [
                {
                    "accessor": "id",
                    "value": "03",
                    "render": "partials/link.html",
                    "class": "link-primary",
                    "props": {"href": "#"},
                },
                {"accessor": "name", "value": "Grace Hopper", "class": "font-bold"},
                {"accessor": "email", "value": "grace@example.com"},
                {"accessor": "role", "value": "Editor"},
                {
                    "accessor": "status",
                    "value": "Invited",
                    "render": "partials/badge.html",
                    "class": "badge-warning",
                },
            ],
        },
    ],
    "page_size_options": [
        {"size": 10, "url": "?page_size=10"},
        {"size": 50, "url": "?page_size=50"},
        {"size": 100, "url": "?page_size=100"},
    ],
    "actions": {
        "top_right": "partials/download_button.html",
        "bottom_right": "partials/add_button.html",
    },
    "pagination": {
        "number": 1,
        "prev_url": None,
        "next_url": "?page=2",
        "paginator": {
            "num_pages": 2,
            "count": 5,
            "per_page": 3,
        },
    },
}


#   class PersonFilterForm(forms.Form):
#       name = forms.CharField(required=False)
#       role = forms.MultipleChoiceField(
#           required=False,
#           choices=Person.Role.choices,
#           widget=forms.CheckboxSelectMultiple,
#       )
#       status = forms.MultipleChoiceField(
#           required=False,
#           choices=Person.Status.choices,
#           widget=forms.CheckboxSelectMultiple,
#       )

#   Then in the view:

#   filter_form = PersonFilterForm(request.GET)

#   context = {
#
#       "table": {
#           "columns": [....],
#       },
#       "filter_form": filter_form,
#       "page_obj": page_obj,
#   }

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
    "page_obj": {  # From here we could get the current page of results, and the pagination info
        "number": 1,
        "has_previous": False,
        "has_next": True,
        "previous_page_number": None,
        "next_page_number": 2,
        "start_index": 1,
        "end_index": 3,
        "paginator": {
            "count": 5,
            "num_pages": 2,
            "per_page": 3,
        },
    },
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
    "filters": [  # object to render the filter menu, created by the meta model
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


def table(request):
    if request.htmx:
        return render(request, "table/partials/table.html", context)
    return render(request, "table/index.html", context)
