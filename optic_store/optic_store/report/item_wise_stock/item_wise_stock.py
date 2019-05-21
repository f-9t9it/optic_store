# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, concatv

from optic_store.utils import pick


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    def make_column(key, label, type="Currency", options=None, width=120):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("brand", "Brand", type="Link", options="Brand"),
        make_column("item_code", "Item", type="Link", options="Item"),
        make_column("item_group", "Item Group", type="Link", options="Item Group"),
        make_column("item_name", "Item Name", type="Data", width=150),
        make_column("standard_selling", "Standard Selling"),
        make_column("qty", "Qty", type="Float"),
        make_column("minimum_selling", "Minumum Selling"),
    ]


def _get_filters(filters):
    clauses = concatv(
        ["disabled = 0"],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["b.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    return " AND ".join(clauses), filters


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                i.brand AS brand,
                i.item_code AS item_code,
                i.item_group AS item_group,
                i.item_name AS item_name,
                ipss.price_list_rate AS standard_selling,
                SUM(b.actual_qty) AS qty,
                ipms.price_list_rate AS minimum_selling
            FROM `tabItem` AS i
            LEFT JOIN `tabBin` AS b ON b.item_code = i.item_code
            LEFT JOIN (
                SELECT * FROM `tabItem Price` WHERE price_list = 'Standard Selling'
            ) AS ipss ON ipss.item_code = i.item_code
            LEFT JOIN (
                SELECT * FROM `tabItem Price` WHERE price_list = 'Minimum Selling'
            ) AS ipms ON ipms.item_code = i.item_code
            WHERE {clauses}
            GROUP BY i.item_code
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
        debug=1,
    )
    return map(partial(pick, keys), items)
