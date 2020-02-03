# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, concatv, merge, unique, groupby, excepts, first

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    query = _get_query(filters)
    data = _get_data(clauses, values, keys, query)
    return columns, data


def _get_columns(filters):
    join_columns = compose(list, concatv)
    return join_columns(
        [
            make_column("posting_date", type="Date", width=90),
            make_column("posting_time", type="Time", width=90),
            make_column("invoice", type="Link", options="Sales Invoice"),
            make_column("customer", type="Link", options="Customer"),
            make_column("customer_name", width=150),
            # simplest way to ignore user permissions is to not make fieldtype Link
            make_column("branch"),
        ],
        [
            make_column("item_code", type="Link", options="Item"),
            make_column("item_name", width=150),
            make_column("item_group", type="Link", options="Item Group"),
            make_column("brand", type="Link", options="Brand"),
            make_column("rate", type="Currency", width=90),
            make_column("qty", type="Float", width=90),
            make_column("amount", type="Currency", width=90),
        ]
        if cint(filters.item_wise)
        else [make_column("grand_total", type="Currency", width=90)],
        [
            make_column("sales_order", "Order", type="Link", options="Sales Order"),
            make_column("order_status", width=150),
            make_column("mops", "Modes of Payment", width=150),
        ],
    )


def _get_filters(filters):
    clauses = concatv(
        [
            "si.docstatus = 1",
            "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
            "si.customer = %(customer)s",
        ],
        ["si.os_branch = %(branch)s"] if filters.branch else [],
    )
    values = merge(
        pick(["customer", "branch"], filters),
        {
            "from_date": filters.date_range[0],
            "to_date": filters.date_range[1],
            "item_wise": cint(filters.item_wise),
        },
    )
    return " AND ".join(clauses), values


def _get_query(filters):
    common_fields = """
        si.posting_date AS posting_date,
        si.posting_time AS posting_time,
        si.name AS invoice,
        si.customer AS customer,
        si.customer_name AS customer_name,
        si.os_branch AS branch,
    """
    if cint(filters.item_wise):
        return """
            SELECT
                {common_fields}
                sii.item_code AS item_code,
                sii.item_name AS item_name,
                sii.item_group AS item_group,
                sii.brand AS brand,
                sii.rate AS rate,
                sii.qty AS qty,
                sii.amount AS amount
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Item` AS sii ON
                sii.parent = si.name
            WHERE {{clauses}}
            ORDER BY si.name, sii.idx
        """.format(
            common_fields=common_fields
        )
    return """
        SELECT
            {common_fields}
            IF(
                si.rounded_total > 0,
                si.rounded_total,
                si.grand_total
            ) AS grand_total
        FROM `tabSales Invoice` AS si
        WHERE {{clauses}}
        ORDER BY si.name
    """.format(
        common_fields=common_fields
    )


def _get_data(clauses, values, keys, query):
    rows = frappe.db.sql(query.format(clauses=clauses), values=values, as_dict=1)

    make_row = compose(partial(pick, keys), _set_mops(rows), _set_sales_orders(rows))
    return with_report_generation_time([make_row(x) for x in rows], keys)


def _set_sales_orders(rows):
    get_orders = compose(
        partial(groupby, "invoice"),
        partial(unique, key=lambda x: x.get("invoice")),
        lambda x: frappe.db.sql(
            """
            SELECT
                sii.parent AS invoice,
                sii.sales_order AS sales_order,
                so.workflow_state AS order_status
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Order` AS so ON so.name = sii.sales_order
            WHERE sii.parent IN %(invoices)s
        """,
            values={"invoices": x},
            as_dict=1,
        ),
        list,
        unique,
        partial(pluck, "invoice"),
    )

    orders = get_orders(rows)
    set_sales_order = compose(
        excepts(StopIteration, first, lambda _: {}),
        lambda x: orders.get(x, []),
        lambda x: x.get("invoice"),
    )

    def fn(row):
        return merge(row, set_sales_order(row))

    return fn


def _set_mops(rows):
    get_mops = compose(
        partial(groupby, "invoice"),
        partial(unique, key=lambda x: x.get("invoice")),
        lambda x: frappe.db.sql(
            """
            SELECT
                sip.parent AS invoice,
                sip.mode_of_payment AS mode_of_payment
            FROM `tabSales Invoice Payment` AS sip
            WHERE sip.parent IN %(invoices)s
            UNION ALL
            SELECT
                per.reference_name AS invoice,
                pe.mode_of_payment AS mode_of_payments
            FROM `tabPayment Entry Reference` AS per
            LEFT JOIN `tabPayment Entry` AS pe ON pe.name = per.parent
            WHERE pe.docstatus = 1 AND per.reference_name IN %(invoices)s
        """,
            values={"invoices": x},
            as_dict=1,
        ),
        list,
        unique,
        partial(pluck, "invoice"),
    )

    mops = get_mops(rows)
    set_mops = compose(
        lambda x: {"mops": ", ".join(x)},
        partial(pluck, "mode_of_payment"),
        lambda x: mops.get(x, []),
        lambda x: x.get("invoice"),
    )

    def fn(row):
        return merge(row, set_mops(row))

    return fn
