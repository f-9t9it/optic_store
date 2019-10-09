# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import concatv, merge

from optic_store.utils import mapf


def execute(filters=None):
    from erpnext.stock.report.stock_ledger.stock_ledger import execute

    columns, data = execute(filters)
    return _get_columns(columns), _get_data(data)


def _get_columns(columns):
    return list(
        concatv(
            columns[:15],
            [
                {
                    "fieldname": "purpose",
                    "fieldtype": "Data",
                    "width": 100,
                    "label": "Purpose",
                },
                {
                    "fieldname": "reference_stock_transfer",
                    "fieldtype": "Link",
                    "width": 110,
                    "label": "Stock Transfer",
                    "options": "Stock Transfer",
                },
            ],
            columns[15:],
        )
    )


def _get_data(data):
    def get_reference_st(stock_entry):
        return frappe.db.exists(
            "Stock Transfer", {"outgoing_stock_entry": stock_entry}
        ) or frappe.db.exists("Stock Transfer", {"outgoing_stock_entry": stock_entry})

    def add_fields(row):
        if row.voucher_type == "Stock Entry":
            purpose = frappe.db.get_value("Stock Entry", row.voucher_no, "purpose")
            return frappe._dict(
                merge(
                    row,
                    {
                        "purpose": purpose,
                        "reference_stock_transfer": get_reference_st(row.voucher_no)
                        if purpose == "Material Transfer"
                        else None,
                    },
                )
            )
        return row

    return mapf(add_fields, data)
