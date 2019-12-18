# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import compose, pluck, valmap, groupby, merge, concatv

from optic_store.utils import sum_by, pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    columns = [
        make_column("posting_date", "Date", type="Date", width=90),
        make_column("net_total", type="Currency"),
        make_column("tax_total", type="Currency"),
        make_column("grand_total", type="Currency"),
        make_column("returns grand_total", "Returns Total", type="Currency"),
    ]
    mops = pluck("name", frappe.get_all("Mode of Payment"))
    return (
        columns
        + [make_column(x, type="Currency") for x in mops]
        + [make_column("total_collected", type="Currency")]
    )


def _get_filters(filters):
    branches = (
        compose(
            list,
            partial(filter, lambda x: x),
            partial(map, lambda x: x.strip()),
            lambda x: x.split(","),
        )(filters.branch)
        if filters.branch
        else None
    )
    clauses = concatv(
        ["s.docstatus = 1", "s.posting_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["s.os_branch IN %(branches)s"] if branches else [],
    )
    values = merge(
        pick(["from_date", "to_date"], filters),
        {"branches": branches} if branches else {},
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                SUM(si.base_net_total) AS net_total,
                SUM(si.base_total_taxes_and_charges) AS tax_total,
                SUM(si.base_grand_total) AS grand_total,
                SUM(sr.base_grand_total) AS returns_grand_total
            FROM `tabSales Invoice` as s
            LEFT JOIN (
                SELECT * FROM `tabSales Invoice` WHERE is_return = 0
            ) AS si ON si.name = s.name
            LEFT JOIN (
                SELECT * from `tabSales Invoice` WHERE is_return = 1
            ) AS sr ON sr.name = s.name
            WHERE {clauses}
            GROUP BY s.posting_date
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )
    si_payments = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                p.mode_of_payment AS mode_of_payment,
                SUM(p.base_amount) AS amount
            FROM `tabSales Invoice` as s
            LEFT JOIN `tabSales Invoice Payment` AS p ON p.parent = s.name
            WHERE {clauses}
            GROUP BY s.posting_date, p.mode_of_payment
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )
    pe_payments = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                s.mode_of_payment AS mode_of_payment,
                IFNULL(SUM(pr.paid_amount), 0) - IFNULL(SUM(pp.paid_amount), 0)
                    AS amount
            FROM `tabPayment Entry` AS s
            LEFT JOIN (
                SELECT * FROM `tabPayment Entry` WHERE payment_type = 'Pay'
            ) AS pp ON pp.name = s.name
            LEFT JOIN (
                SELECT * from `tabPayment Entry` WHERE payment_type = 'Receive'
            ) AS pr ON pr.name = s.name
            WHERE s.party_type = 'Customer' AND {clauses}
            GROUP BY s.posting_date, s.mode_of_payment
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})

    make_row = compose(
        partial(valmap, lambda x: x or None),
        partial(pick, keys),
        partial(merge, template),
        _set_payments(si_payments + pe_payments),
    )

    return with_report_generation_time([make_row(x) for x in items], keys)


def _set_payments(payments):
    mop_map = compose(
        partial(valmap, sum_by("amount")),
        partial(groupby, ("mode_of_payment")),
        partial(filter, lambda x: x.get("amount") is not None),
    )

    payments_grouped = compose(
        partial(valmap, mop_map), partial(groupby, "posting_date")
    )(payments)

    def fn(row):
        mops = payments_grouped[row.get("posting_date")]
        return merge(row, mops, {"total_collected": sum(mops.values())})

    return fn
