# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, valmap

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

    return [
        make_column("branch", type="Link", options="Branch"),
        make_column("item_group", type="Link", options="Item Group"),
        make_column("brand", type="Link", options="Brand"),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=180),
        make_column("qty_sold", type="Float", width=90),
        make_column("qty_balance", "Balance Qty", type="Float", width=90),
    ]


def _get_filters(filters):
    branches = split_to_list(filters.branches)
    clauses = concatv(
        ["si.docstatus = 1"],
        ["si.posting_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["si.os_branch IN %(branches)s"] if branches else [],
        ["sii.brand = %(brand)s"] if filters.brand else [],
        ["sii.item_code = %(item_code)s"] if filters.item_code else [],
        ["sii.item_group = %(item_group)s"] if filters.item_group else [],
        ["INSTR(sii.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    values = merge(filters, {"branches": branches} if branches else {})
    return " AND ".join(clauses), values


@with_report_error_check
def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                si.os_branch AS branch,
                sii.item_group AS item_group,
                sii.brand AS brand,
                sii.item_code AS item_code,
                sii.item_name AS item_name,
                SUM(sii.qty) AS qty_sold,
                bin.projected_qty AS qty_balance
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Item` AS sii ON
                sii.parent = si.name
            LEFT JOIN `tabBranch` as br ON
                br.name = si.os_branch
            LEFT JOIN `tabBin` AS bin ON
                bin.item_code = sii.item_code AND
                bin.warehouse = br.warehouse
            WHERE {clauses}
            GROUP BY si.os_branch, sii.item_code
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(pick, keys),
        partial(valmap, lambda x: x or None),
        partial(merge, template),
    )

    return map(make_row, items)
