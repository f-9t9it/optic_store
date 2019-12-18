# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import today
from functools import partial
from toolz import compose, pluck

from optic_store.utils import pick
from optic_store.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("loyalty_card_no"),
        make_column("customer", type="Link", options="Customer"),
        make_column("customer_name", width=150),
        make_column("cpr_no", width=90),
        make_column("mobile_no", options="Phone"),
        make_column("points", type="Int", width=90),
        make_column("activation_date", type="Date", width=90),
        make_column("loyalty_program", type="Link", options="Loyalty Program"),
        make_column("tier"),
    ]


def _get_filters(filters):
    return "", {}


def _get_data(clauses, values, keys):
    rows = frappe.db.sql(
        """
            SELECT
                c.name AS customer,
                c.customer_name AS customer_name,
                c.os_cpr_no AS cpr_no,
                c.os_mobile_number AS mobile_no,
                c.os_loyalty_card_no AS loyalty_card_no,
                c.os_loyalty_activation_date AS activation_date,
                c.loyalty_program AS loyalty_program,
                c.loyalty_program_tier AS tier,
                lpe.loyalty_points AS points
            FROM `tabCustomer` AS c
            LEFT JOIN (
                SELECT
                    customer,
                    loyalty_program,
                    SUM(loyalty_points) AS loyalty_points
                FROM `tabLoyalty Point Entry`
                WHERE expiry_date >= %(today)s
                GROUP BY customer, loyalty_program
            ) AS lpe ON
                lpe.customer = c.name AND
                lpe.loyalty_program = c.loyalty_program
            WHERE IFNULL(c.loyalty_program, '') != ''
            ORDER BY c.os_loyalty_activation_date
        """,
        values={"today": today()},
        as_dict=1,
    )

    make_row = partial(pick, keys)
    return [make_row(x) for x in rows]
