# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, concatv

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("sales_no"),
        make_column("date"),
        make_column("description", width=150),
        make_column("qty", "Quantity"),
        make_column("item_sold_at"),
        make_column("total_sales_invoice"),
        make_column("sales_person"),
        make_column("customer_name", "Customer", width=150),
        make_column("customer", "Customer ID", type="Link", options="Customer"),
        make_column("old_customer_id", "Old Customer ID"),
        make_column("branch"),
    ]


def _get_filters(filters):
    join_clauses = compose(lambda x: " AND ".join(x), concatv)

    return (
        join_clauses(
            ["True"], ["osr.customer = %(customer)s"] if filters.customer else []
        ),
        filters,
    )


def _get_data(clauses, values, keys):
    result = frappe.db.sql(
        """
            SELECT
                osri.sales_no AS sales_no,
                osri.date AS date,
                osri.description AS description,
                osri.qty AS qty,
                osri.item_sold_at AS item_sold_at,
                osri.total_sales_invoice AS total_sales_invoice,
                osri.sales_person AS sales_person,
                osr.customer_name AS customer_name,
                osr.customer AS customer,
                osr.old_customer_id AS old_customer_id,
                osri.branch_code AS branch
            FROM `tabOld Sales Record Item` AS osri
            LEFT JOIN `tabOld Sales Record` AS osr ON osr.name = osri.parent
            WHERE {clauses}
            ORDER BY osri.date
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )
    make_row = compose(partial(pick, keys))
    return with_report_generation_time([make_row(x) for x in result], keys)
