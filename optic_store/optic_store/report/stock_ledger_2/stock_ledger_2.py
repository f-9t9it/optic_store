# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import concatv, merge, compose, pluck

from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    from erpnext.stock.report.stock_ledger.stock_ledger import execute

    columns, data = execute(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    return _get_columns(columns), _get_data(data, keys)


def _get_columns(columns):
    return list(
        concatv(
            columns[:15],
            [
                make_column("purpose"),
                make_column(
                    "reference_stock_transfer",
                    "Stock Transfer",
                    type="Link",
                    options="Stock Transfer",
                ),
            ],
            columns[15:],
        )
    )


def _get_data(data, keys):
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

    return with_report_generation_time([add_fields(x) for x in data], keys)
