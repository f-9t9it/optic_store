# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, merge

from optic_store.utils import pick
from optic_store.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("branch", type="Link", options="Branch", width=120),
        make_column("qty_sold", type="Float"),
        make_column("cost_price", type="Currency", width=120),
        make_column("sale_amount", type="Currency", width=120),
        make_column("cost_pc", label="Cost %", type="Percent"),
    ]


def _get_filters(filters):
    clauses = [
        "si.docstatus = 1",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    price_clauses = [
        "ip.item_code = sii.item_code",
        "ip.price_list = %(buying_price_list)s",
    ]
    values = {
        "from_date": filters.date_range[0],
        "to_date": filters.date_range[1],
        "buying_price_list": frappe.db.get_single_value(
            "Buying Settings", "buying_price_list"
        )
        or "Standard Buying",
    }
    return (
        {
            "clauses": " AND ".join(clauses),
            "price_clauses": " AND ".join(price_clauses),
        },
        values,
    )


def _get_data(clauses, values, keys):
    rows = frappe.db.sql(
        """
            SELECT
                si.os_branch AS branch,
                SUM(sii.qty) AS qty_sold,
                SUM(ip.price_list_rate * sii.qty) AS cost_price,
                SUM(sii.amount) AS sale_amount
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Item` AS sii ON
                sii.parent = si.name
            LEFT JOIN `tabItem Price` AS ip ON {price_clauses}
            WHERE {clauses}
            GROUP BY si.os_branch
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_cost_pc(row):
        cost_pc = (
            (row.get("cost_price") or 0) / row.get("sale_amount") * 100
            if row.get("sale_amount")
            else 0
        )
        return merge(row, {"cost_pc": cost_pc})

    make_row = compose(partial(pick, keys), set_cost_pc)
    return [make_row(x) for x in rows]
