# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, merge, concatv

from optic_store.utils import pick, with_report_error_check, split_to_list, key_by
from optic_store.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
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

    join_clauses = compose(lambda x: " AND ".join(x), concatv)
    clauses = join_clauses(
        ["TRUE"],
        ["branch.name IN %(branches)s"] if branches else [],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.item_code = %(item_code)s"] if filters.item_code else [],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["INSTR(i.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    si_clauses = join_clauses(
        ["si.docstatus = 1", "si.posting_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["si.os_branch IN %(branches)s"] if branches else [],
    )
    values = merge(filters, {"branches": branches} if branches else {})
    return (
        {
            "clauses": clauses,
            "group_by": "bin.item_code, branch.name" if branches else "bin.item_code",
            "si_clauses": si_clauses,
            "si_group_by": "sii.item_code, si.os_branch"
            if branches
            else "sii.item_code",
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
                SUM(bin.projected_qty) AS qty_balance
            FROM `tabBin` AS bin
            LEFT JOIN `tabBranch` as branch ON
                branch.warehouse = bin.warehouse
            LEFT JOIN `tabItem` AS i ON
                i.name = bin.item_code
            WHERE {clauses}
            GROUP BY {group_by}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    sold_items = frappe.db.sql(
        """
            SELECT
                sii.item_code AS item_code,
                si.os_branch AS branch,
                SUM(sii.qty) AS qty_sold
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON
                si.name = sii.parent
            WHERE {si_clauses}
            GROUP BY {si_group_by}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    width_branch = not not values.get("branches")
    make_row = compose(
        partial(pick, keys), _make_add_qty_sold(sold_items, width_branch)
    )

    make_data = compose(
        list,
        partial(
            filter, lambda x: x.get("qty_sold", 0) != 0 or x.get("qty_balance", 0) != 0
        ),
        partial(map, make_row),
    )

    return make_data(items)


def _make_add_qty_sold(items, with_branch):
    group_fn = (
        (lambda x: (x.get("item_code"), x.get("branch")))
        if with_branch
        else lambda x: x.get("item_code")
    )

    grouped = key_by(group_fn, items)

    def fn(row):
        return merge(row, grouped.get(group_fn(row), {}))

    return fn
