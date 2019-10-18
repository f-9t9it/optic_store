# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, concatv

from optic_store.utils import pick, mapf


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
        ["i.disabled = 0"],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["INSTR(i.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    bin_clauses = concatv(
        ["b.item_code = i.item_code"],
        ["b.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    return (
        {"clauses": " AND ".join(clauses), "bin_clauses": " AND ".join(bin_clauses)},
        filters,
    )


def price_sq(price_list):
    return """
        SELECT item_code, AVG(price_list_rate) AS price_list_rate
        FROM `tabItem Price`
        WHERE price_list = '{price_list}'
        GROUP BY item_code
    """.format(
        price_list=price_list
    )


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
            LEFT JOIN `tabBin` AS b ON {bin_clauses}
            LEFT JOIN ({standard_selling_sq}) AS ipss ON ipss.item_code = i.item_code
            LEFT JOIN ({minimum_selling_sq}) AS ipms ON ipms.item_code = i.item_code
            WHERE {clauses}
            GROUP BY i.item_code
        """.format(
            standard_selling_sq=price_sq("Standard Selling"),
            minimum_selling_sq=price_sq("Minimum Selling"),
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    return mapf(partial(pick, keys), items)
