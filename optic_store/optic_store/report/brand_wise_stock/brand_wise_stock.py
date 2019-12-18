# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, concatv

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    return [
        make_column("brand", type="Link", options="Brand", width=180),
        make_column("item_group", type="Link", options="Item Group", width=180),
        make_column("qty", type="Float"),
    ]


def _get_filters(filters):
    clauses = concatv(
        ["i.disabled = 0"],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
    )
    bin_clauses = concatv(
        ["b.item_code = i.item_code"],
        ["b.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    return (
        {"clauses": " AND ".join(clauses), "bin_clauses": " AND ".join(bin_clauses)},
        filters,
    )


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                i.brand AS brand,
                i.item_group AS item_group,
                SUM(b.projected_qty) AS qty
            FROM `tabItem` AS i
            LEFT JOIN `tabBin` AS b ON {bin_clauses}
            WHERE {clauses}
            GROUP BY i.brand, i.item_group
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    make_row = partial(pick, keys)
    return with_report_generation_time([make_row(x) for x in items], keys)
