# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today, getdate
from functools import partial
from toolz import merge, pluck, keyfilter, compose


def execute(filters=None):
    args = _get_args(filters)
    columns = _get_columns(args)
    keys = _get_keys(args)
    data = _get_data(args, keys)
    return columns, data


def _get_args(filters={}):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    return merge(
        filters,
        {
            "query_date": filters.get("query_date") or today(),
            "price_list1": frappe.db.get_value(
                "Buying Settings", None, "buying_price_list"
            )
            or "Standard Buying",
            "price_list2": frappe.db.get_value(
                "Selling Settings", None, "selling_price_list"
            )
            or "Standard Selling",
        },
    )


def _get_columns(args):
    def make_column(key, label, type="Currency", options=None, width=120):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    columns = [
        make_column("supplier", "Supplier", type="Link", options="Supplier"),
        make_column("brand", "Brand", type="Link", options="Brand"),
        make_column("item_code", "Item Code", type="Link", options="Item"),
        make_column("item_name", "Item Name", type="Data", width=200),
        make_column("batch_no", "Batch", type="Link", options="Batch"),
        make_column("expiry_date", "Expiry Date", type="Date", width=90),
        make_column("expiry_in_days", "Expiry in Days", type="Int", width=90),
        make_column("qty", "Quantity", type="Float", width=90),
        make_column("price1", args.get("price_list1")),
        make_column("price2", args.get("price_list2")),
    ]
    return columns


def _get_keys(args):
    return compose(list, partial(pluck, "fieldname"), _get_columns)(args)


def _get_data(args, keys):
    sles = frappe.db.sql(
        """
            SELECT
                sle.batch_no AS batch_no,
                sle.item_code AS item_code,
                sle.warehouse AS warehouse,
                SUM(sle.actual_qty) AS qty,
                i.item_name AS item_name,
                i.brand AS brand,
                id.default_supplier AS supplier,
                b.expiry_date AS expiry_date,
                p1.price_list_rate AS price1,
                p2.price_list_rate AS price2
            FROM `tabStock Ledger Entry` AS sle
            LEFT JOIN `tabItem` AS i ON
                i.item_code = sle.item_code
            LEFT JOIN `tabBatch` AS b ON
                b.batch_id = sle.batch_no
            LEFT JOIN `tabItem Price` AS p1 ON
                p1.item_code = sle.item_code AND
                p1.price_list = %(price_list1)s
            LEFT JOIN `tabItem Price` AS p2 ON
                p2.item_code = sle.item_code AND
                p2.price_list = %(price_list2)s
            LEFT JOIN `tabItem Default` AS id ON
                id.parent = sle.item_code AND
                id.company = sle.company
            WHERE
                sle.docstatus = 1 AND
                sle.company = %(company)s AND
                sle.posting_date <= %(query_date)s AND
                IFNULL(sle.batch_no, '') != ''
            GROUP BY sle.batch_no, sle.warehouse
            ORDER BY sle.item_code, sle.warehouse
        """,
        values=args,
        as_dict=1,
    )

    def set_expiry(row):
        expiry_in_days = (row.expiry_date - getdate()).days if row.expiry_date else None
        return merge(row, {"expiry_in_days": expiry_in_days})

    make_row = compose(partial(keyfilter, lambda k: k in keys), set_expiry)

    return map(make_row, sles)
