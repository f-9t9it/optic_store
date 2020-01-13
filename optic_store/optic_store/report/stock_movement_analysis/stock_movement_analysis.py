# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, concatv, merge, groupby

from optic_store.utils import pick, key_by
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("item_group", type="Link", options="Item Group"),
        make_column("brand", type="Link", options="Brand"),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=150),
        make_column("opening_qty", type="Int", width=90),
        make_column("purchased_qty", type="Int", width=90),
        make_column("transit_qty", type="Int", width=90),
        make_column("returned_qty", type="Int", width=90),
        make_column("adjustments", type="Int", width=90),
        make_column("sold_qty", type="Int", width=90),
        make_column("total", type="Int", width=90),
        make_column("current_qty", type="Int", width=90),
    ]


def _get_filters(filters):
    join_columns = compose(lambda x: " AND ".join(x), concatv)
    item_clauses = join_columns(
        ["i.disabled = 0"],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.name = %(item_code)s"] if filters.item_code else [],
        ["INSTR(i.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    sle_clauses = join_columns(
        ["sle.posting_date BETWEEN %(start_date)s AND %(end_date)s"]
    )

    def get_dates():
        query_date = frappe.utils.getdate(filters.query_date)
        if filters.period == "Monthly":
            return {
                "start_date": frappe.utils.get_first_day(query_date),
                "end_date": frappe.utils.get_last_day(query_date),
            }
        if filters.period == "Yearly":
            return {
                "start_date": query_date.replace(month=1, day=1),
                "end_date": query_date.replace(month=12, day=31),
            }
        frappe.throw(_("Unknown period"))

    values = merge(
        pick(["item_group", "brand", "item_code", "item_name"], filters), get_dates()
    )
    return {"item_clauses": item_clauses, "sle_clauses": sle_clauses}, values


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                i.item_group AS item_group,
                i.brand AS brand,
                i.name AS item_code,
                i.item_name AS item_name,
                SUM(bin.projected_qty) AS current_qty
            FROM `tabItem` AS i
            LEFT JOIN `tabBin` AS bin
                ON bin.item_code = i.name
            WHERE {item_clauses}
            GROUP BY i.item_code
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    sles = frappe.db.sql(
        """
            SELECT
                sle.item_code AS item_code,
                sle.voucher_type AS voucher_type,
                pi.is_return AS purchase_invoice_is_return,
                pr.is_return AS purchase_receipt_is_return,
                se.purpose AS stock_entry_purpose,
                st.workflow_state AS stock_transfer_status,
                sle.actual_qty AS qty
            FROM `tabStock Ledger Entry` AS sle
            LEFT JOIN `tabStock Entry` AS se
                ON se.name = sle.voucher_no
            LEFT JOIN `tabPurchase Invoice` AS pi
                ON pi.name = sle.voucher_no
            LEFT JOIN `tabPurchase Receipt` AS pr
                ON pr.name = sle.voucher_no
            LEFT JOIN `tabStock Transfer` AS st
                ON st.name = se.os_reference_stock_transfer
            WHERE {sle_clauses}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_total(row):
        def get(field):
            return row.get(field) or 0

        return merge(
            row,
            {
                "total": get("opening_qty")
                + get("purchased_qty")
                + get("transit_qty")
                - get("returned_qty")
                - get("adjustments")
                - get("sold_qty")
            },
        )

    make_row = compose(
        partial(pick, keys), set_total, _set_qtys(sles), _set_opening(values)
    )
    return with_report_generation_time([make_row(x) for x in items], keys)


def _set_opening(values):
    opening = key_by(
        "item_code",
        frappe.db.sql(
            """
                SELECT
                    item_code AS item_code,
                    SUM(actual_qty) AS qty
                FROM `tabStock Ledger Entry`
                WHERE posting_date < %(start_date)s
                GROUP BY item_code
            """,
            values=values,
            as_dict=1,
        ),
    )

    def fn(row):
        return merge(
            row, {"opening_qty": opening.get(row.get("item_code"), {}).get("qty")},
        )

    return fn


def _set_qtys(sles):
    sles_by_item_code = groupby("item_code", sles)

    def aggregate(key, filter_fn):
        return sum(
            [x.get("qty") for x in sles_by_item_code.get(key, []) if filter_fn(x)]
        )

    def purchase_filter(row):
        return (
            row.get("voucher_type") in ["Purchase Invoice", "Purchase Receipt"]
            and not row.get("purchase_invoice_is_return")
            and not row.get("purchase_receipt_is_return")
        )

    def transit_filter(row):
        return (
            row.get("voucher_type") == "Stock Entry"
            and row.get("stock_entry_purpose") == "Material Transfer"
            and row.get("stock_transfer_status") == "In Transit"
            and row.get("qty") > 0
        )

    def returned_filter(row):
        return row.get("voucher_type") in ["Purchase Invoice", "Purchase Receipt"] and (
            row.get("purchase_invoice_is_return")
            or row.get("purchase_receipt_is_return")
        )

    def adjustment_filter(row):
        return (
            row.get("voucher_type") == "Stock Entry"
            and row.get("stock_entry_purpose") != "Material Transfer"
        )

    def sold_filter(row):
        return row.get("voucher_type") in ["Sales Invoice", "Delivery Note"]

    def fn(row):
        item_code = row.get("item_code")
        return merge(
            row,
            {
                "purchased_qty": aggregate(item_code, purchase_filter),
                "transit_qty": aggregate(item_code, transit_filter),
                "returned_qty": -aggregate(item_code, returned_filter),
                "adjustments": -aggregate(item_code, adjustment_filter),
                "sold_qty": -aggregate(item_code, sold_filter),
            },
        )

    return fn
