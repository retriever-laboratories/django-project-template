from django.shortcuts import render


TABLE_SPEC = {
    "id": "users",
    "filters_applied": True,
    "filters": [
        {"accessor": "name", "label": "Name", "type": "text", "values": ["Ada", "Grace"]},
        {"accessor": "email", "label": "Email", "type": "text", "values": []},
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
            "values": ["active"],
        },
    ],
    "columns": [
        {
            "accessor": "name",
            "label": "Name",
            "sort": {
                "enabled": True,
                "direction": "asc",
            },
        },
        {
            "accessor": "email",
            "label": "Email",
            "sort": {
                "enabled": True,
                "direction": None,
            },
        },
        {
            "accessor": "role",
            "label": "Role",
            "sort": {
                "enabled": True,
                "direction": None,
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
                {"accessor": "name", "value": "Ada Lovelace"},
                {"accessor": "email", "value": "ada@example.com"},
                {"accessor": "role", "value": "Admin"},
                {
                    "accessor": "status",
                    "value": "Active",
                    "render": {"template": "components/badge.html", "class": "badge badge-xs badge-soft badge-success"},
                },
            ],
        },
        {
            "id": 2,
            "cells": [
                {"accessor": "name", "value": "Alan Turing"},
                {"accessor": "email", "value": "alan@example.com"},
                {"accessor": "role", "value": "Editor"},
                {
                    "accessor": "status",
                    "value": "Active",
                    "render": {"template": "components/badge.html", "class": "badge badge-xs badge-soft badge-success"},
                },
            ],
        },
        {
            "id": 3,
            "cells": [
                {"accessor": "name", "value": "Grace Hopper"},
                {"accessor": "email", "value": "grace@example.com"},
                {"accessor": "role", "value": "Editor"},
                {
                    "accessor": "status",
                    "value": "Invited",
                    "render": {"template": "components/badge.html", "class": "badge badge-xs badge-soft badge-warning"},
                },
            ],
        },
    ],
    "page_size_options": [10, 50, 100],
    "pagination": {
        "number": 1,
        "has_previous": False,
        "previous_page_number": None,
        "has_next": True,
        "next_page_number": 2,
        "paginator": {
            "num_pages": 2,
            "count": 5,
            "per_page": 3,
        },
    },
}


def table(request):
    context = {
        "table": TABLE_SPEC,
    }
    return render(request, "table/index.html", {"context": context})
