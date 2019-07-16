# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, merge, concatv

from optic_store.utils import pick, with_report_error_check, split_to_list


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    columns = concatv(
        [make_column("branch", type="Link", options="Branch")]
        if filters.branches
        else [],
        [
            make_column("item_group", type="Link", options="Item Group"),
            make_column("brand", type="Link", options="Brand"),
            make_column("item_code", type="Link", options="Item"),
            make_column("item_name", width=180),
            make_column("qty_sold", "Sold Qty", type="Float", width=90),
            make_column("qty_balance", "Balance Qty", type="Float", width=90),
        ],
    )
    return list(columns)


def _get_filters(filters):
    branches = split_to_list(filters.branches)
    clauses = concatv(
        ["TRUE"],
        ["branch.name IN %(branches)s"] if branches else [],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.item_code = %(item_code)s"] if filters.item_code else [],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["INSTR(i.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    si_clauses = concatv(
        ["si.docstatus = 1", "si.posting_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["si.os_branch IN %(branches)s"] if branches else [],
    )
    values = merge(filters, {"branches": branches} if branches else {})
    return (
        {
            "clauses": " AND ".join(clauses),
            "si_clauses": " AND ".join(si_clauses),
            "group_by": "bin.item_code, branch.name" if branches else "bin.item_code",
        },
        values,
    )


@with_report_error_check
def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                branch.name AS branch,
                i.item_group AS item_group,
                i.brand AS brand,
                bin.item_code AS item_code,
                i.item_name AS item_name,
                SUM(sii.qty) AS qty_sold,
                SUM(bin.projected_qty) AS qty_balance
            FROM `tabBin` AS bin
            LEFT JOIN `tabBranch` as branch ON
                branch.warehouse = bin.warehouse
            LEFT JOIN `tabItem` AS i ON
                i.name = bin.item_code
            LEFT JOIN (
                SELECT
                    sii.item_code AS item_code,
                    SUM(sii.qty) AS qty
                FROM `tabSales Invoice Item` AS sii
                LEFT JOIN `tabSales Invoice` AS si ON
                    si.name = sii.parent
                WHERE {si_clauses}
                GROUP BY sii.item_code
            ) AS sii ON
                sii.item_code = bin.item_code
            WHERE {clauses}
            GROUP BY {group_by}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
        debug=1,
    )

    make_data = compose(
        partial(map, partial(pick, keys)),
        partial(filter, lambda x: x.qty_sold != 0 or x.qty_balance != 0),
    )

    return make_data(items)
