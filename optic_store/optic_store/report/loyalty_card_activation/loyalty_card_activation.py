# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, excepts, groupby, flip, get, first

from optic_store.utils import pick, split_to_list
from optic_store.utils.helpers import generate_intervals
from optic_store.utils.report import make_column


def execute(filters=None):
    intervals = generate_intervals(
        filters.interval, filters.date_range[0], filters.date_range[1]
    )
    columns = _get_columns(filters, intervals)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys, intervals)
    return columns, data


def _get_columns(filters, intervals):
    join_columns = compose(list, concatv)
    return join_columns(
        [make_column("branch", type="Link", options="Branch")],
        [
            merge(x, make_column(x.get("key"), x.get("label"), width=90))
            for x in intervals
        ],
        [make_column("total", type="Int", width=90)],
    )


def _get_filters(filters):
    branches = split_to_list(filters.branches)
    branch_clause = concatv(
        ["disabled = 0"], ["branch IN %(branches)s"] if branches else []
    )
    customer_clause = concatv(
        ["os_loyalty_activation_date BETWEEN %(from_date)s AND %(to_date)s"],
        ["branch IN %(branches)s"] if branches else [],
    )
    values = merge(
        {"from_date": filters.date_range[0], "to_date": filters.date_range[1]},
        {"branches": branches} if branches else {},
    )
    return (
        {
            "branch_clause": " AND ".join(branch_clause),
            "customer_clause": " AND ".join(customer_clause),
        },
        values,
    )


def _get_data(clauses, values, keys, intervals):
    branches = frappe.db.sql(
        """
            SELECT branch
            FROM `tabBranch` WHERE {branch_clause}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    customers = frappe.db.sql(
        """
            SELECT
                branch,
                os_loyalty_activation_date AS loyalty_activation_date
            FROM `tabCustomer`
            WHERE {customer_clause}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    make_row = compose(partial(pick, keys), _count_activations(customers, intervals))

    return [make_row(x) for x in branches]


def _count_activations(customers, intervals):
    def groupby_filter(c):
        def fn(p):
            return (
                p.get("start_date")
                <= c.get("loyalty_activation_date")
                <= p.get("end_date")
            )

        return fn

    groupby_fn = compose(
        partial(get, "key", default=None),
        excepts(StopIteration, first, lambda __: {}),
        partial(flip, filter, intervals),
        groupby_filter,
    )

    customers_grouped = groupby(groupby_fn, customers)

    def seg_filter(x):
        return lambda c: c.get("branch") == x

    segregator_fns = [
        merge(
            x,
            {
                "seger": compose(
                    len,
                    partial(flip, filter, get(x.get("key"), customers_grouped, [])),
                    seg_filter,
                )
            },
        )
        for x in intervals
    ]

    def seg_reducer(branch):
        def fn(a, p):
            key = get("key", p, None)
            seger = get("seger", p, lambda __: None)
            return merge(a, {key: seger(branch)})

        return fn

    total_fn = compose(len, partial(flip, filter, customers), seg_filter)

    def fn(x):
        branch = x.get("branch")
        return merge(
            x,
            reduce(seg_reducer(branch), segregator_fns, {}),
            {"total": total_fn(branch)},
        )

    return fn
