# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck

from optic_store.utils import pick


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("loyalty_card_no"),
        make_column("customer", type="Link", options="Customer"),
        make_column("customer_name", width=150),
        make_column("cpr_no", width=90),
        make_column("mobile_no", options="Phone"),
        make_column("points_earned", type="Int", width=90),
        make_column("date_earned", type="Date", width=90),
        make_column("points_redeemed", type="Int", width=90),
        make_column("expiry_date", type="Date", width=90),
    ]


def _get_filters(filters):
    clauses = [
        "lpe.expiry_date >= %(expiry_date)s",
        "IFNULL(lpe.redeem_against, '') = ''",
    ]
    return " AND ".join(clauses), filters


def _get_data(clauses, values, keys):
    rows = frappe.db.sql(
        """
            SELECT
                c.os_loyalty_card_no AS loyalty_card_no,
                lpe.customer AS customer,
                c.customer_name AS customer_name,
                c.os_cpr_no AS cpr_no,
                c.os_mobile_number AS mobile_no,
                c.os_loyalty_activation_date AS activation_date,
                c.loyalty_program AS loyalty_program,
                c.loyalty_program_tier AS tier,
                lpe.loyalty_points AS points_earned,
                -lper.loyalty_points AS points_redeemed,
                lpe.posting_date AS date_earned,
                lpe.expiry_date AS expiry_date
            FROM `tabLoyalty Point Entry` AS lpe
            LEFT JOIN `tabCustomer` AS c ON c.name = lpe.customer
            LEFT JOIN (
                SELECT
                    redeem_against,
                    SUM(loyalty_points) AS loyalty_points
                FROM `tabLoyalty Point Entry`
                WHERE IFNULL(redeem_against, '') != ''
                GROUP BY redeem_against
            ) AS lper ON lper.redeem_against = lpe.name
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    make_row = partial(pick, keys)
    return [make_row(x) for x in rows]
