# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, keyfilter, valmap, groupby, merge


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    data = _get_data(filters, keys)
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

    columns = [
        make_column("posting_date", "Date", type="Date", width=90),
        make_column("total", "Total"),
        make_column("net_total", "Net Total"),
        make_column("tax_total", "Tax Total"),
        make_column("returns_net_total", "Returns Net"),
    ]
    mops = pluck("name", frappe.get_all("Mode of Payment"))
    return columns + map(lambda x: make_column(x, x), mops)


def _get_data(args, keys):
    clauses = """
        s.docstatus = 1 AND
        s.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """
    items = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                SUM(si.base_total) AS total,
                SUM(si.base_net_total) AS net_total,
                SUM(si.base_total_taxes_and_charges) AS tax_total,
                SUM(si.base_change_amount) AS change_amount,
                SUM(sr.base_net_total) AS returns_net_total
            FROM `tabSales Invoice` as s
            LEFT JOIN (
                SELECT * FROM `tabSales Invoice` WHERE is_return = 0
            ) AS si ON si.name = s.name
            LEFT JOIN (
                SELECT * from `tabSales Invoice` WHERE is_return = 1
            ) AS sr ON sr.name = s.name
            WHERE {clauses}
            GROUP BY s.posting_date
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )
    payments = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                p.mode_of_payment AS mode_of_payment,
                SUM(p.base_amount) AS amount
            FROM `tabSales Invoice` as s
            LEFT JOIN `tabSales Invoice Payment` as p ON p.parent = s.name
            WHERE {clauses}
            GROUP BY s.posting_date, p.mode_of_payment
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )

    make_row = compose(
        partial(valmap, lambda x: x or None),
        partial(keyfilter, lambda k: k in keys),
        _set_payments(payments),
    )

    return map(make_row, items)


def _set_payments(payments):
    mop_map = compose(
        partial(
            valmap,
            compose(sum, partial(map, lambda x: x or 0), partial(pluck, "amount")),
        ),
        partial(groupby, ("mode_of_payment")),
    )

    payments_grouped = compose(
        partial(valmap, mop_map), partial(groupby, "posting_date")
    )(payments)

    def fn(row):
        mop_payments = payments_grouped[row.get("posting_date")]
        cash_amount = (mop_payments.get("Cash") or 0) - (row.get("change_amount") or 0)
        return merge(row, mop_payments, {"Cash": cash_amount})

    return fn
