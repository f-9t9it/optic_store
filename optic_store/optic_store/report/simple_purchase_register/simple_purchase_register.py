# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, keyfilter, concatv


def execute(filters=None):
    columns = _get_columns()
    keys = _get_keys()
    data = _get_data(_get_clauses(filters), filters, keys)
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
        make_column("invoice", "Invoice No", type="Link", options="Purchase Invoice"),
        make_column("supplier", "Supplier", type="Link", options="Supplier"),
        make_column("total", "Total"),
        make_column("discount", "Discount"),
        make_column("net_total", "Net Total"),
        make_column("tax", "Tax"),
        make_column("grand_total", "Grand Total"),
    ]
    return columns


def _get_keys():
    return compose(list, partial(pluck, "fieldname"), _get_columns)()


def _get_clauses(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    invoice_type = {"Purchases": 0, "Returns": 1}
    clauses = concatv(
        [
            "docstatus = 1",
            "company = %(company)s",
            "posting_date BETWEEN %(from_date)s AND %(to_date)s",
        ],
        ["supplier = %(supplier)s"] if filters.get("supplier") else [],
        ["is_return = {}".format(invoice_type[filters.get("invoice_type")])]
        if filters.get("invoice_type") in invoice_type
        else [],
    )
    return " AND ".join(clauses)


def _get_data(clauses, args, keys):
    items = frappe.db.sql(
        """
            SELECT
                posting_date,
                name AS invoice,
                supplier,
                base_total AS total,
                base_discount_amount AS discount,
                base_net_total AS net_total,
                base_total_taxes_and_charges AS tax,
                base_grand_total AS grand_total
            FROM `tabPurchase Invoice`
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )
    make_row = partial(keyfilter, lambda k: k in keys)
    return [make_row(x) for x in items]
