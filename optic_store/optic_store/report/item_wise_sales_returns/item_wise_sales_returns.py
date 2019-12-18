# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, merge, pluck, keyfilter

from optic_store.utils.report import make_column


def execute(filters=None):
    columns = _get_columns()
    keys = _get_keys()
    data = _get_data(_get_clauses(filters), filters, keys)
    return columns, data


def _get_columns():
    return [
        make_column("customer", type="Link", options="Customer"),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=180),
        make_column("qty", "Returned Qty", type="Float", width=90),
        make_column("rate", type="Currency"),
        make_column("gross", type="Currency"),
    ]


def _get_keys():
    return compose(list, partial(pluck, "fieldname"), _get_columns)()


def _get_clauses(filters):
    clauses = [
        "si.docstatus = 1",
        "si.is_return = 1",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    if filters.get("customer"):
        clauses.append("si.customer = %(customer)s")
    return " AND ".join(clauses)


def _get_data(clauses, args, keys):
    items = frappe.db.sql(
        """
            SELECT
                si.customer AS customer,
                sii.item_code AS item_code,
                sii.item_name AS item_name,
                SUM(sii.qty) AS qty,
                SUM(sii.amount) AS gross
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
            WHERE {clauses}
            GROUP BY si.customer, sii.item_code
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )

    def add_rate(row):
        return merge(row, {"rate": row.gross / row.qty})

    make_row = compose(partial(keyfilter, lambda k: k in keys), add_rate)

    return [make_row(x) for x in items]
