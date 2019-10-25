# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import (
    compose,
    pluck,
    merge,
    concatv,
    excepts,
    groupby,
    flip,
    get,
    first,
    accumulate,
)

from optic_store.utils import pick, split_to_list
from optic_store.utils.helpers import generate_intervals


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
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

    return [
        make_column("posting_date", type="Date"),
        make_column("voucher_type", type="Link", options="Doctype", width=120),
        make_column(
            "voucher_no", type="Dynamic Link", options="voucher_type", width=120
        ),
        make_column("points", type="Int"),
        make_column("balance", type="Int"),
    ]


def _get_filters(filters):
    # branches = split_to_list(filters.branches)
    opening_clause = concatv(
        ["posting_date < %(from_date)s"],
        ["customer = %(customer)s"] if filters.customer else [],
        ["loyalty_program = %(loyalty_program)s"] if filters.loyalty_program else [],
    )
    period_clause = concatv(
        ["posting_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["customer = %(customer)s"] if filters.customer else [],
        ["loyalty_program = %(loyalty_program)s"] if filters.loyalty_program else [],
    )
    values = merge(
        pick(["customer", "loyalty_program"], filters),
        {"from_date": filters.date_range[0], "to_date": filters.date_range[1]},
    )
    return (
        {
            "opening_clause": " AND ".join(opening_clause),
            "period_clause": " AND ".join(period_clause),
        },
        values,
    )


def _get_data(clauses, values, keys):
    def get_query(query):
        return frappe.db.sql(query.format(**clauses), values=values, as_dict=1)

    get_opening = compose(lambda x: x.opening, first, get_query)

    opening = get_opening(
        """
            SELECT SUM(loyalty_points) AS opening
            FROM `tabLoyalty Point Entry`
            WHERE {opening_clause}
        """
    )

    rows = get_query(
        """
            SELECT
                posting_date,
                sales_invoice,
                os_custom_loyalty_entry AS custom_loyalty_entry,
                loyalty_points AS points
            FROM `tabLoyalty Point Entry`
            WHERE {period_clause}
            ORDER BY posting_date
        """
    )

    def set_voucher_ref(row):
        if row.get("sales_invoice"):
            return merge(
                row,
                {
                    "voucher_type": "Sales Invoice",
                    "voucher_no": row.get("sales_invoice"),
                },
            )
        if row.get("custom_loyalty_entry"):
            return merge(
                row,
                {
                    "voucher_type": "Custom Loyalty Entry",
                    "voucher_no": row.get("custom_loyalty_entry"),
                },
            )
        return row

    def set_balance(a, row):
        return merge(row, {"balance": a.get("balance") + row.get("points")})

    make_list = compose(list, concatv)
    return make_list(
        accumulate(
            set_balance,
            [set_voucher_ref(x) for x in rows],
            initial={"voucher_no": "Opening", "balance": opening},
        ),
        [{"voucher_no": "Total", "points": sum([x.points for x in rows])}],
    )
