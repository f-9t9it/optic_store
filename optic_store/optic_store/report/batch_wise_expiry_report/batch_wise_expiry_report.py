# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from functools import partial
from toolz import merge, pluck, compose, concatv

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    filters_extended = merge(
        filters,
        {
            "is_manager": any(
                role in ["Item Manager", "Stock Manager"] for role in frappe.get_roles()
            ),
            "buying_price_list": frappe.db.get_value(
                "Buying Settings", None, "buying_price_list"
            )
            or "Standard Buying",
            "selling_price_list": frappe.db.get_value(
                "Selling Settings", None, "selling_price_list"
            )
            or "Standard Selling",
        },
    )

    columns = _get_columns(filters_extended)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters_extended)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    join_columns = compose(list, concatv)
    return join_columns(
        [make_column("supplier", type="Link", options="Supplier")]
        if filters.get("is_manager")
        else [],
        [
            make_column("brand", type="Link", options="Brand"),
            make_column("item_code", type="Link", options="Item"),
            make_column("item_name", width=200),
            make_column("item_group", type="Link", options="Item Group"),
            make_column("warehouse", type="Link", options="Warehouse"),
            make_column("batch_no", "Batch", type="Link", options="Batch"),
            make_column("expiry_date", type="Date", width=90),
            make_column("expiry_in_days", "Expiry in Days", type="Int", width=90),
            make_column("qty", "Quantity", type="Float", width=90),
        ],
        [make_column("buying_price", filters.get("buying_price_list"), type="Currency")]
        if filters.get("is_manager")
        else [],
        [
            make_column(
                "selling_price", filters.get("selling_price_list"), type="Currency"
            )
        ],
    )


def _get_filters(filters):
    clauses = concatv(
        [
            "sle.docstatus = 1",
            "sle.company = %(company)s",
            "sle.posting_date <= %(query_date)s",
            "IFNULL(sle.batch_no, '') != ''",
        ],
        ["sle.warehouse = %(warehouse)s"] if filters.get("warehouse") else [],
        ["i.item_group = %(item_group)s"] if filters.get("item_group") else [],
    )
    values = pick(
        [
            "company",
            "query_date",
            "warehouse",
            "item_group",
            "buying_price_list",
            "selling_price_list",
            "hide_zero_stock",
        ],
        filters,
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    sles = frappe.db.sql(
        """
            SELECT
                sle.batch_no AS batch_no,
                sle.item_code AS item_code,
                SUM(sle.actual_qty) AS qty,
                sle.warehouse AS warehouse,
                i.item_name AS item_name,
                i.item_group AS item_group,
                i.brand AS brand,
                id.default_supplier AS supplier,
                b.expiry_date AS expiry_date,
                p1.price_list_rate AS buying_price,
                p2.price_list_rate AS selling_price
            FROM `tabStock Ledger Entry` AS sle
            LEFT JOIN `tabItem` AS i ON
                i.item_code = sle.item_code
            LEFT JOIN `tabBatch` AS b ON
                b.batch_id = sle.batch_no
            LEFT JOIN `tabItem Price` AS p1 ON
                p1.item_code = sle.item_code AND
                p1.price_list = %(buying_price_list)s
            LEFT JOIN `tabItem Price` AS p2 ON
                p2.item_code = sle.item_code AND
                p2.price_list = %(selling_price_list)s
            LEFT JOIN `tabItem Default` AS id ON
                id.parent = sle.item_code AND
                id.company = sle.company
            WHERE {clauses}
            GROUP BY sle.batch_no, sle.warehouse
            ORDER BY sle.item_code, sle.warehouse
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_expiry(row):
        expiry_in_days = (row.expiry_date - getdate()).days if row.expiry_date else None
        return merge(row, {"expiry_in_days": expiry_in_days})

    make_row = compose(partial(pick, keys), set_expiry)

    def row_filter(row):
        if not values.get("hide_zero_stock"):
            return True
        return row.get("qty") > 0

    return with_report_generation_time(
        [make_row(x) for x in sles if row_filter(x)], keys
    )
