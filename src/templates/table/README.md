# Table Spec

The table partials render one object called `table`.

The spec should already contain the final UI state: columns, rows, filters, sort state, actions, and pagination URLs. Templates only read the spec and render it.

## Basic Example

```json
{
  "id": "users",
  "columns": [
    {
      "accessor": "name",
      "label": "Name",
      "sort": {
        "enabled": true,
        "direction": "asc",
        "asc_url": "/table/?sort=name",
        "desc_url": "/table/?sort=-name"
      }
    },
    {
      "accessor": "status",
      "label": "Status",
      "sort": {
        "enabled": false
      }
    }
  ],
  "rows": [
    {
      "id": 1,
      "cells": [
        {
          "accessor": "name",
          "value": "Ada Lovelace",
          "class": "font-bold"
        },
        {
          "accessor": "status",
          "value": "Active",
          "render": "components/badge.html",
          "class": "badge-success"
        }
      ]
    }
  ],
  "filters": [],
  "filters_applied": false,
  "actions": {},
  "pagination": null
}
```

## Root Fields

| Field | Required | Description |
| --- | --- | --- |
| `id` | Yes | HTML id suffix for the table wrapper. |
| `columns` | Yes | Header definition. |
| `rows` | Yes | Body rows and cells. |
| `filters` | No | Filter menu items. Empty list hides filter options. |
| `filters_base_url` | No | URL used by the filter form and clear button. |
| `filters_applied` | No | Shows active filter badges and controls clear state. |
| `page_size_options` | No | Page size dropdown options. |
| `actions` | No | Template slots for fixed actions. |
| `pagination` | No | Pagination state. `null` hides pagination. |

## Columns

Each column describes one header cell.

| Field | Description |
| --- | --- |
| `accessor` | Stable key for the column. |
| `label` | Text shown in the header. |
| `sort.enabled` | Shows or hides the sort button. |
| `sort.direction` | Current sort state: `"asc"`, `"desc"`, or `null`. |
| `sort.asc_url` | HTMX URL for ascending sort. |
| `sort.desc_url` | HTMX URL for descending sort. |

If `sort.enabled` is `false`, the header renders only the label.

## Rows And Cells

Rows are rendered in order. Cells are also rendered in order.

| Field | Description |
| --- | --- |
| `row.id` | Optional row id rendered as `data-row-id`. |
| `row.cells` | List of cells for that row. |
| `cell.accessor` | Column key for the cell. |
| `cell.value` | Display value. |
| `cell.class` | Optional CSS classes. |
| `cell.render` | Optional template path for custom rendering. |
| `cell.props` | Optional data passed to the custom render template. |

Use `cell.render` for special column styles, for example:

```json
{
  "accessor": "status",
  "value": "Active",
  "render": "components/badge.html",
  "class": "badge-success"
}
```

## Filters

Each filter describes one filter panel.

| Field | Description |
| --- | --- |
| `accessor` | Query parameter name and filter key. |
| `label` | Text shown in the filter menu. |
| `type` | Filter partial name. Current values: `"text"` and `"select"`. |
| `values` | Selected values. Text filters can have multiple values. |
| `options` | Select choices. Only needed for `type: "select"`. |
| `badges` | Active filter chips. |
| `badge.remove_url` | HTMX URL to remove that filter value. |

Example:

```json
{
  "accessor": "role",
  "label": "Role",
  "type": "select",
  "options": [
    { "value": "admin", "label": "Admin" },
    { "value": "editor", "label": "Editor" }
  ],
  "values": ["admin"],
  "badges": [
    { "value": "admin", "remove_url": "/table/" }
  ]
}
```

## Pagination

Pagination uses a small object based on Django pagination.

```json
{
  "number": 1,
  "prev_url": null,
  "next_url": "/table/?page=2",
  "paginator": {
    "num_pages": 2,
    "count": 5,
    "per_page": 3
  }
}
```

`page_size_options` is optional:

```json
[
  { "size": 10, "url": "/table/?page_size=10" },
  { "size": 50, "url": "/table/?page_size=50" }
]
```

## Actions

Actions are optional template slots.

```json
{
  "top_right": "components/download_button.html",
  "bottom_right": "components/add_button.html"
}
```

Slots:

- `top_right`
- `bottom_left`
- `bottom_right`

## Partials

| Partial | Reads |
| --- | --- |
| `table/partials/table.html` | Main `table` object. |
| `table/partials/table_top.html` | Filters and top actions. |
| `table/partials/table_header.html` | Columns and sort state. |
| `table/partials/table_rows.html` | Rows and cells. |
| `table/partials/pagination.html` | Pagination and page size options. |
| `table/partials/table_bottom.html` | Bottom actions. |

