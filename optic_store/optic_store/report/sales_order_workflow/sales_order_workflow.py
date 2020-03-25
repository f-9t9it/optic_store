# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from functools import partial
from toolz import compose, pluck, concatv, merge, groupby, valmap, unique

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    join = compose(list, concatv)
    workflow_states = frappe.get_all(
        "Workflow Document State",
        filters={"parent": "Optic Store Sales Order"},
        fields="state",
        order_by="idx",
    )
    return join(
        [make_column("sales_order", type="Link", options="Sales Order", width=150)],
        [
            make_column(x, type="Datetime", width=180)
            for x in pluck("state", workflow_states)
        ],
        [
            make_column("lab_tech", width=150),
            make_column("total", type="Currency"),
            make_column("outstanding", type="Currency"),
        ],
    )


def _get_filters(filters):
    join = compose(lambda x: " AND ".join(x), concatv)
    clauses = join(
        ["True"],
        ["so.os_branch = %(branch)s"] if filters.branch else [],
        ["so.workflow_state != 'Collected'"] if not filters.show_collected else [],
    )
    values = merge(
        pick(["branch"], filters),
        {"from_date": filters.date_range[0], "to_date": filters.date_range[1]},
    )
    return clauses, values


def _get_data(clauses, values, keys):
    get_sales_orders = compose(list, unique, partial(pluck, "name"), frappe.db.sql)
    sales_orders = get_sales_orders(
        """
            SELECT docname AS name FROM `tabVersion`
            WHERE
                ref_doctype = 'Sales Order' AND
                INSTR(data, 'comment_type') > 0 AND
                INSTR(data, 'Workflow') > 0 AND
                creation BETWEEN %(from_date)s AND %(to_date)s
            UNION ALL
            SELECT name FROM `tabSales Order`
            WHERE
                creation BETWEEN %(from_date)s AND %(to_date)s
        """,
        values=values,
        as_dict=1,
    )

    result = frappe.db.sql(
        """
            SELECT
                so.name AS sales_order,
                so.creation AS creation,
                e.employee_name AS lab_tech,
                so.grand_total AS total
            FROM `tabSales Order` AS so
            LEFT JOIN `tabEmployee` AS e ON e.name = so.os_lab_tech
            WHERE so.name IN %(sales_orders)s AND {clauses}
            ORDER BY so.creation
        """.format(
            clauses=clauses
        ),
        values=merge(values, {"sales_orders": sales_orders}),
        as_dict=1,
    )

    set_outstanding = _set_outstanding_amounts(result)
    set_workflow_updates = _set_workflow_updates(result)

    make_row = compose(partial(pick, keys), set_workflow_updates, set_outstanding)
    return with_report_generation_time([make_row(x) for x in result], keys)


def _set_outstanding_amounts(result):
    outstanding_amounts = (
        {
            k: v
            for k, v in frappe.db.sql(
                """
                    SELECT
                        DISTINCT sii.sales_order AS sales_order,
                        si.outstanding_amount AS outstanding
                    FROM `tabSales Invoice` AS si
                    LEFT JOIN `tabSales Invoice Item` AS sii ON sii.parent = si.name
                    WHERE sii.sales_order IN %(sales_orders)s
                """,
                values={"sales_orders": [x.get("sales_order") for x in result]},
            )
        }
        if result
        else {}
    )

    def fn(row):
        sales_order = row.get("sales_order")
        return merge(row, {"outstanding": outstanding_amounts.get(sales_order, 0)})

    return fn


def _set_workflow_updates(result):
    get_comments = compose(
        partial(
            valmap,
            lambda comments: {x.get("comment"): x.get("creation") for x in comments},
        ),
        partial(groupby, "docname"),
        partial(map, lambda x: pick(["docname", "creation", "comment"], x)),
        partial(filter, lambda x: x.get("comment_type") == "Workflow"),
        partial(map, lambda x: merge(x, json.loads(x.get("data", "{}")))),
    )
    versions = frappe.db.sql(
        """
            SELECT docname, creation, data
            FROM `tabVersion`
            WHERE ref_doctype = 'Sales Order' AND docname IN %(sales_orders)s
        """,
        values={"sales_orders": [x.get("sales_order") for x in result]},
        as_dict=1,
    )
    comments = get_comments(versions)

    def fn(row):
        docname = row.get("sales_order")
        return merge(row, {"Draft": row.get("creation")}, comments.get(docname, {}))

    return fn
