# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, concatv, merge

from optic_store.utils import pick, split_to_list
from optic_store.utils.report import make_column, with_report_generation_time
from optic_store.api.customer import get_user_branch


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    return list(
        concatv(
            [
                make_column("outgoing_date", type="Date", width=90),
                make_column("incoming_date", type="Date", width=90),
                make_column(
                    "name", "Doc Name", type="Link", options="Stock Transfer", width=150
                ),
                make_column("workflow_state", "Status", width=90),
                make_column("item_code", type="Link", options="Item", width=150),
                make_column("item_name", width=180),
                make_column("qty", type="Float", width=90),
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
        if (
            any(role in ["Branch User", "Branch Stock"] for role in frappe.get_roles())
            and user_branch
        ):
            return [user_branch]

        frappe.throw(_("Manager privilege or Branch User / Branch Stock role required"))

    branches = get_branches()

    clauses = concatv(
        [
            "st.outgoing_datetime <= %(to_date)s",
            "IFNULL(st.incoming_datetime, CURRENT_DATE) >= %(from_date)s",
        ],
        ["st.docstatus = 1"] if not cint(filters.show_all) else [],
        ["(st.source_branch IN %(branches)s OR st.target_branch IN %(branches)s)"]
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
                st.name AS name,
                st.outgoing_datetime AS outgoing_datetime,
                st.incoming_datetime AS incoming_datetime,
                st.source_branch AS source_branch,
                st.target_branch AS target_branch,
                sti.item_code AS item_code,
                sti.item_name AS item_name,
                sti.qty AS qty,
                st.outgoing_stock_entry AS outgoing_stock_entry,
                st.incoming_stock_entry AS incoming_stock_entry,
                st.workflow_state AS workflow_state
            FROM `tabStock Transfer` AS st
            RIGHT JOIN `tabStock Transfer Item` AS sti ON
                sti.parent = st.name
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
    return with_report_generation_time([make_row(x) for x in docs], keys)
