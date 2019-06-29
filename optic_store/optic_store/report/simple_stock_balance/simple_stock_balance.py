# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, valmap

from optic_store.utils import pick


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label, type="Float", options=None, width=90):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("item_code", "Item Code", type="Link", options="Item"),
        make_column("item_name", "Item Name", type="Data", width=180),
        make_column("actual_qty", "Actual Qty"),
        make_column("reserved_qty", "Reserved Qty"),
        make_column("ordered_qty", "Ordered Qty"),
        make_column("projected_qty", "Projected Qty"),
    ]


def _get_filters(filters):
    scrap_warehouse = frappe.db.get_single_value(
        "Optical Store Settings", "scrap_warehouse"
    )
    clauses = ["i.disabled = 0"]
    bin_clauses = concatv(
        ["TRUE"],
        ["warehouse = %(warehouse)s"] if filters.warehouse else [],
        ["warehouse != '{}'".format(scrap_warehouse)] if scrap_warehouse else [],
    )
    return (
        {"clauses": " AND ".join(clauses), "bin_clauses": " AND ".join(bin_clauses)},
        filters,
    )


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                i.item_code AS item_code,
                i.item_name AS item_name,
                b.actual_qty AS actual_qty,
                b.reserved_qty AS reserved_qty,
                b.ordered_qty AS ordered_qty,
                b.projected_qty AS projected_qty
            FROM `tabItem` AS i
            LEFT JOIN (
                SELECT
                    item_code,
                    SUM(actual_qty) AS actual_qty,
                    SUM(reserved_qty) AS reserved_qty,
                    SUM(ordered_qty) AS ordered_qty,
                    SUM(projected_qty) AS projected_qty
                FROM `tabBin`
                WHERE {bin_clauses}
                GROUP BY item_code
            ) AS b ON b.item_code = i.item_code
            WHERE {clauses}
        """.format(
            **clauses
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

    return map(make_row, items)
