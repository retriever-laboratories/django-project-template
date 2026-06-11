from django.shortcuts import render


TABLE_SPEC = {
    "id": "users",
    "filters": [
        {"accessor": "name", "label": "Name", "type": "text", "value": None},
        {"accessor": "email", "label": "Email", "type": "text", "value": None},
        {
            "accessor": "role",
            "label": "Role",
            "type": "select",
            "options": [
                {"value": "admin", "label": "Admin"},
                {"value": "editor", "label": "Editor"},
                {"value": "viewer", "label": "Viewer"},
            ],
            "value": None,
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
            "value": None,
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
                {"accessor": "status", "value": "Active"},
            ],
        },
        {
            "id": 2,
            "cells": [
                {"accessor": "name", "value": "Alan Turing"},
                {"accessor": "email", "value": "alan@example.com"},
                {"accessor": "role", "value": "Editor"},
                {"accessor": "status", "value": "Active"},
            ],
        },
        {
            "id": 3,
            "cells": [
                {"accessor": "name", "value": "Grace Hopper"},
                {"accessor": "email", "value": "grace@example.com"},
                {"accessor": "role", "value": "Editor"},
                {"accessor": "status", "value": "Invited"},
            ],
        },
    ],
    "pagination": {
        "number": 1,
        "has_other_pages": True,
        "has_previous": False,
        "previous_page_number": None,
        "has_next": True,
        "next_page_number": 2,
        "paginator": {
            "num_pages": 2,
            "page_range": [1, 2],
        },
    },
}


def table(request):
    context = {
        "table": TABLE_SPEC,
    }
    return render(request, "table/index.html", {"context": context})
