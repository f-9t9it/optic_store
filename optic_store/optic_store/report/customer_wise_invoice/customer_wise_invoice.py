# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, concatv, merge

from optic_store.utils import pick, mapf


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    query = _get_query(filters)
    data = _get_data(clauses, values, keys, query)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=90):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    join_columns = compose(list, concatv)
    return join_columns(
        [
            make_column("posting_date", type="Date"),
            make_column("posting_time", type="Time"),
            make_column("invoice", type="Link", options="Sales Invoice", width=120),
            make_column("customer", type="Link", options="Customer", width=120),
            make_column("customer_name", width=150),
            # simplest way to ignore user permissions is to not make fieldtype Link
            make_column("branch", width=120),
        ],
        [
            make_column("item_code", type="Link", options="Item", width=120),
            make_column("item_name", width=150),
            make_column("rate", type="Currency"),
            make_column("amount", type="Currency"),
        ]
        if cint(filters.item_wise)
        else [make_column("grand_total", type="Currency")],
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
                sii.rate AS rate,
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

    make_row = partial(pick, keys)
    return mapf(make_row, rows)
