# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, valmap

from optic_store.utils import pick
from optic_store.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", type="Data", width=180),
        make_column("actual_qty", type="Float", width=90),
        make_column("reserved_qty", type="Float", width=90),
        make_column("projected_qty", type="Float", width=90),
        make_column("warehouse", type="Link", options="Warehouse"),
    ]


def _get_filters(filters):
    scrap_warehouse = frappe.db.get_single_value(
        "Optical Store Settings", "scrap_warehouse"
    )
    clauses = concatv(
        ["i.disabled = 0"],
        ["warehouse = %(warehouse)s"] if filters.warehouse else [],
        ["warehouse != '{}'".format(scrap_warehouse)] if scrap_warehouse else [],
    )
    return " AND ".join(clauses), filters


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                b.item_code AS item_code,
                i.item_name AS item_name,
                b.actual_qty AS actual_qty,
                b.reserved_qty AS reserved_qty,
                b.projected_qty AS projected_qty,
                b.warehouse
            FROM `tabBin` AS b
            LEFT JOIN `tabItem` AS i  ON i.item_code = b.item_code
            WHERE {clauses}
            ORDER BY b.item_code
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(pick, keys),
        partial(valmap, lambda x: x or None),
        partial(merge, template),
    )

    return [make_row(x) for x in items]
