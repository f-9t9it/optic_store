# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, valmap, groupby

from optic_store.utils import pick, split_to_list, sum_by


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    def make_column(key, label, type="Data", options=None, width=120):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    columns = [
        make_column("item_group", "Item Group", type="Link", options="Item Group"),
        make_column("brand", "Brand", type="Link", options="Brand"),
        make_column("item_code", "Item Code", type="Link", options="Item"),
        make_column("item_name", "Item Name", width=180),
        make_column("minimum_selling", "Minimum Selling", type="Currency", width=90),
        make_column("standard_selling", "Standard Selling", type="Currency", width=90),
    ]
    branches = pluck("name", frappe.get_all("Branch", filters={"disabled": 0}))
    return (
        columns
        + map(lambda x: make_column(x, x, type="Float", width=90), branches)
        + [make_column("total_qty", "Total Qty", type="Float", width=90)]
    )


def _get_filters(filters):
    item_groups = split_to_list(filters.item_groups)
    brands = split_to_list(filters.brands)
    item_codes = split_to_list(filters.item_codes)
    clauses = concatv(
        ["i.disabled = 0"],
        ["i.item_group IN %(item_groups)s"] if item_groups else [],
        ["i.brand IN %(brands)s"] if brands else [],
        ["i.item_code IN %(item_codes)s"] if item_codes else [],
        # TODO: fix error when item_name is not found
        ["INSTR(i.item_name, %(item_name)s) > 0"] if filters.item_name else [],
    )
    values = merge(
        pick(["item_name"], filters),
        {"item_groups": item_groups} if item_groups else {},
        {"brands": brands} if brands else {},
        {"item_codes": item_codes} if item_codes else {},
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                i.item_group AS item_group,
                i.brand AS brand,
                i.item_code AS item_code,
                i.item_name AS item_name,
                ipms.price_list_rate AS minimum_selling,
                ipss.price_list_rate AS standard_selling
            FROM `tabItem` AS i
            LEFT JOIN (
                SELECT * FROM `tabItem Price` WHERE price_list = 'Minimum Selling'
            ) AS ipms ON ipms.item_code = i.item_code
            LEFT JOIN (
                SELECT * FROM `tabItem Price` WHERE price_list = 'Standard Selling'
            ) AS ipss ON ipss.item_code = i.item_code
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
        debug=1,
    )
    bins = frappe.db.sql(
        """
            SELECT
                b.item_code AS item_code,
                b.actual_qty AS qty,
                w.branch AS branch
            FROM `tabBin` AS b
            LEFT JOIN `tabBranch` AS w ON w.warehouse = b.warehouse
            WHERE b.item_code IN %(items)s
        """,
        values={"items": list(pluck("item_code", items))},
        as_dict=1,
    )

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(valmap, lambda x: x or None),
        partial(pick, keys),
        partial(merge, template),
        _set_qty(bins),
    )

    return map(make_row, items)


def _set_qty(bins):
    grouped = groupby("item_code", bins)
    get_total = sum_by("qty")

    def fn(item):
        branches = grouped.get(item.get("item_code"))
        return (
            merge(
                item,
                {x.get("branch"): x.get("qty") for x in branches},
                {"total_qty": get_total(branches)},
            )
            if branches
            else item
        )

    return fn
