# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, concatv, merge

from optic_store.utils import pick, split_to_list
from optic_store.api.customer import get_user_branch


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    def make_column(key, label, type="Data", options=None, width=90):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return list(
        concatv(
            [
                make_column("outgoing_date", "Outgoing Date", type="Date"),
                make_column("incoming_date", "Incoming Date", type="Date"),
                make_column(
                    "name", "Doc Name", type="Link", options="Stock Transfer", width=150
                ),
                make_column("workflow_state", "Status"),
                make_column("total_qty", "Total Qty", type="Float"),
            ],
            [
                make_column(
                    "outgoing_stock_entry",
                    "Outgoing Doc",
                    type="Link",
                    options="Stock Entry",
                    width=150,
                ),
                make_column(
                    "incoming_stock_entry",
                    "Incoming Doc",
                    type="Link",
                    options="Stock Entry",
                    width=150,
                ),
            ]
            if any(role in ["Accounts Manager"] for role in frappe.get_roles())
            else [],
        )
    )


def _get_filters(filters):
    def get_branches():
        if any(role in ["Accounts Manager"] for role in frappe.get_roles()):
            return split_to_list(filters.branches)
        user_branch = get_user_branch()
        if any(role in ["Branch User"] for role in frappe.get_roles()) and user_branch:
            return [user_branch]

        frappe.throw(_("Manager privilege or Branch User role required"))

    branches = get_branches()

    clauses = concatv(
        [
            "outgoing_datetime <= %(to_date)s",
            "IFNULL(incoming_datetime, CURRENT_DATE) >= %(from_date)s",
        ],
        ["docstatus = 1"] if not cint(filters.show_all) else [],
        ["(source_branch IN %(branches)s OR target_branch IN %(branches)s)"]
        if branches
        else [],
    )
    values = merge(
        pick(["from_date", "to_date"], filters),
        {"branches": branches} if branches else {},
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    docs = frappe.db.sql(
        """
            SELECT
                name,
                outgoing_datetime,
                incoming_datetime,
                source_branch,
                target_branch,
                total_qty,
                outgoing_stock_entry,
                incoming_stock_entry,
                workflow_state
            FROM `tabStock Transfer`
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values,
        as_dict=1,
    )

    def add_dates(x):
        return merge(
            x,
            {
                "outgoing_date": x.outgoing_datetime.date()
                if x.outgoing_datetime
                else None,
                "incoming_date": x.incoming_datetime.date()
                if x.incoming_datetime
                else None,
            },
        )

    make_row = compose(partial(pick, keys), add_dates)
    return map(make_row, docs)
