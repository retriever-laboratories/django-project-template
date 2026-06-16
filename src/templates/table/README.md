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

## Root Object

Required fields:

- `id`: unique string for this table instance. The root partial uses it for the wrapper id `table-{id}`, the real `<table id="{id}">`, and the HTMX target.
- `columns`: list of header definitions. The order of this list is the visible header order.
- `rows`: list of row definitions. If the list is empty, the table body renders the empty state.

Recommended fields:

- `filters`: list of filter definitions. If empty or missing, the filter menu is not shown.
- `filters_base_url`: URL used by the filter form and the clear-all button. It should preserve any state that must survive filtering, for example the current sort.
- `filters_applied`: boolean. When true, the top partial renders filter badges and enables the clear-all UI.
- `actions`: dictionary of optional template slots. Use `{}` when there are no actions.
- `pagination`: pagination object. Use `null` when pagination should be hidden.
- `page_size_options`: list of page-size choices. It is only read when `pagination` exists.

## Columns

Each item in `columns` renders one `<th>`.

- `accessor`: stable key for the column. Keep it aligned with the matching cell accessor and with related filter/sort params.
- `label`: text rendered in the header.
- `sort`: object that controls the sort UI for this column.

Sort fields:

- `enabled`: boolean. If false, the header renders only `label`.
- `direction`: current direction for this column. Use `"asc"`, `"desc"`, or `null`.
- `asc_url`: URL requested when the user chooses ascending sort.
- `desc_url`: URL requested when the user chooses descending sort.

The template does not calculate sort state. It only chooses the icon from `direction` and sends HTMX requests to the provided URLs.

## Rows And Cells

Each item in `rows` renders one `<tr>`.

- `id`: optional row identifier. When present, it is rendered as `data-row-id`.
- `cells`: list of cell definitions. Cells are rendered in the exact order provided.

Important: the current row template does not look up cells by column accessor. If the first cell should appear under the first column, it must be first in the `cells` list.

Cell fields:

- `accessor`: stable key for the cell. It should match the related column accessor.
- `value`: display value passed to the default cell renderer or to the custom render partial.
- `class`: optional CSS classes. For default cells, this is applied to `<td>`. For custom cells, it is passed into the render partial as `class`.
- `render`: optional template path. When present, the cell includes that template instead of printing `value` directly.
- `props`: optional dictionary passed to the custom render partial as `props`.

Use `render` when the value needs a reusable presentation, such as a link, badge, formatted amount, or status label:

```json
{
  "accessor": "status",
  "value": "Active",
  "render": "components/badge.html",
  "class": "badge-success"
}
```

For a link cell, pass extra data through `props`:

```json
{
  "accessor": "id",
  "value": "01",
  "render": "components/link.html",
  "class": "link-primary",
  "props": {
    "href": "/users/1/"
  }
}
```

## Filters

Each item in `filters` renders one option inside the filter menu. The selected filter then includes `table/filters/{type}.html`.

- `accessor`: query parameter name and filter key. Text and select inputs use it as the input `name`.
- `label`: text shown in the filter menu and in the active badge group.
- `type`: filter partial name. Current supported values are `"text"` and `"select"`.
- `values`: currently selected values. Use a list even for one value.
- `badges`: active chips for this filter. Each badge is rendered independently.

Text filter notes:

- `values` seeds the Alpine draft list.
- The user can add more than one value before applying.
- Each value becomes a hidden input with `name={accessor}`.

Select filter notes:

- `options` is required.
- Each option needs `value` and `label`.
- An option is checked when its `value` exists in `values`.

Badge fields:

- `value`: text shown in the chip.
- `remove_url`: URL requested when removing that one value. Build this URL with the remaining active filters already included.

Example select filter:

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
    { "value": "admin", "remove_url": "/table/?sort=name" }
  ]
}
```

## Pagination

`pagination` is the already-renderable pagination state. It can be built from Django pagination, but the template only reads this shape:

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

Fields:

- `number`: current page number.
- `prev_url`: URL for the previous page. Use `null` to disable the previous button.
- `next_url`: URL for the next page. Use `null` to disable the next button.
- `paginator.num_pages`: total number of pages.
- `paginator.count`: total number of items across all pages.
- `paginator.per_page`: current page size shown in the page-size button.

`page_size_options` controls the page-size dropdown:

```json
[
  { "size": 10, "url": "/table/?page_size=10" },
  { "size": 50, "url": "/table/?page_size=50" }
]
```

Each option needs:

- `size`: label shown in the dropdown.
- `url`: URL requested when that size is selected.

## Actions

`actions` contains optional template paths used as slots.

```json
{
  "top_right": "components/download_button.html",
  "bottom_right": "components/add_button.html"
}
```

Supported slots:

- `top_right`: rendered on the right side of `table_top.html`.
- `bottom_left`: rendered on the left side of `table_bottom.html`.
- `bottom_right`: rendered on the right side of `table_bottom.html`.

Each action template receives `table`.

## Partial Responsibilities

- `table/partials/table.html`: root wrapper, HTMX target, main table, pagination, and bottom area.
- `table/partials/table_top.html`: filter menu, active filter badges, and top-right action.
- `table/partials/table_header.html`: column loop and sortable/non-sortable header rendering.
- `table/partials/sort.html`: sort icon state and sort menu URLs for one column.
- `table/partials/table_rows.html`: row loop, empty state, default cells, and custom cell renders.
- `table/partials/filters.html`: filter menu shell and dynamic filter partial include.
- `table/filters/text.html`: multi-value text filter draft UI.
- `table/filters/select.html`: checkbox select filter UI.
- `table/partials/filter_badges.html`: active filter badge groups and remove URLs.
- `table/partials/pagination.html`: page navigation and page-size selector.
- `table/partials/table_bottom.html`: bottom-left and bottom-right actions.

