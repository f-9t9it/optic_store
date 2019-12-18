# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import (
    compose,
    pluck,
    valmap,
    groupby,
    merge,
    get,
    concatv,
    unique,
    excepts,
    first,
)

from optic_store.utils import pick, split_to_list
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data, meta = _get_data(clauses, values, keys)
    return columns, data, None, None, meta


def _get_columns():
    columns = [
        make_column("sales_invoice", type="Link", options="Sales Invoice"),
        make_column("posting_time", "Time", type="Time", width=90),
        make_column("customer", type="Link", options="Customer"),
        make_column("customer_name", type="Data", width=150),
        make_column("total_qty", type="Float"),
        make_column("net_total", type="Currency"),
        make_column("tax_total", type="Currency"),
        make_column("grand_total", type="Currency"),
        make_column("outstanding_amount", "Outstanding", type="Currency"),
        make_column("sales_person", type="Link", options="Employee"),
        make_column("sales_person_name", width=150),
        make_column("is_return", type="Check", hidden=1),
        make_column("return_against", type="Link", options="Sales Invoice", hidden=1),
    ]
    mops = pluck("name", frappe.get_all("Mode of Payment"))
    return (
        columns
        + [make_column(x, x) for x in mops]
        + [make_column("total_collected", "Total Collected")]
    )


def _get_filters(filters):
    branches = split_to_list(filters.branch)
    clauses = concatv(
        ["s.docstatus = 1", "s.posting_date = %(posting_date)s"],
        ["s.os_branch IN %(branches)s"] if branches else [],
    )
    values = merge(
        pick(["posting_date"], filters), {"branches": branches} if branches else {}
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                s.name AS sales_invoice,
                s.posting_time AS posting_time,
                s.is_return AS is_return,
                s.return_against AS return_against,
                s.customer AS customer,
                s.customer_name AS customer_name,
                s.total_qty AS total_qty,
                s.base_net_total AS net_total,
                s.base_total_taxes_and_charges AS tax_total,
                s.base_grand_total AS grand_total,
                s.outstanding_amount AS outstanding_amount,
                s.os_sales_person AS sales_person,
                e.employee_name AS sales_person_name
            FROM `tabSales Invoice` AS s
            LEFT JOIN `tabEmployee` AS e ON e.name = s.os_sales_person
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )
    payments = frappe.db.sql(
        """
            SELECT
                p.parent AS sales_invoice,
                p.mode_of_payment AS mode_of_payment,
                p.base_amount AS amount
            FROM `tabSales Invoice` as s
            LEFT JOIN `tabSales Invoice Payment` as p ON p.parent = s.name
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    collection = frappe.db.sql(
        """
            SELECT
                COUNT(s.name) AS pe_count,
                SUM(s.paid_amount) AS pe_amount
            FROM `tabPayment Entry` AS s
            WHERE
                s.payment_type = 'Receive' AND
                s.party_type = 'Customer' AND
                {clauses}
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
        _set_payments(payments),
    )

    make_mops = compose(
        lambda x: {"mops": x}, unique, partial(pluck, "mode_of_payment")
    )
    make_pe = excepts("StopIteration", first, {"pe_count": 0, "pe_amount": 0})
    return (
        with_report_generation_time([make_row(x) for x in items], keys),
        merge(make_mops(payments), make_pe(collection)),
    )


def _set_payments(payments):
    def mop_map(item):
        return reduce(
            lambda a, x: merge(a, {x.get("mode_of_payment"): x.get("amount")}), item, {}
        )

    payments_grouped = compose(
        partial(valmap, mop_map), partial(groupby, "sales_invoice")
    )(payments)

    def fn(row):
        mops = get(row.get("sales_invoice"), payments_grouped, {})
        return merge(row, mops, {"total_collected": sum(mops.values())})

    return fn
