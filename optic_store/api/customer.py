# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck


@frappe.whitelist()
def get_user_branch():
    employee = frappe.db.exists("Employee", {"user_id": frappe.session.user})
    return frappe.db.get_value("Employee", employee, "branch") if employee else None


@frappe.whitelist()
def get_dashboard_data(customer):
    labels = compose(list, partial(pluck, "item_group"), frappe.get_all)(
        "Optical Store Settings Dashboard Item Group",
        fields=["item_group"],
        order_by="idx",
    )
    if not labels:
        return None
    items = frappe.db.sql(
        """
            SELECT
                soi.item_group AS item_group,
                SUM(soi.qty) AS qty,
                SUM(soi.amount) AS amount
            FROM `tabSales Order Item` AS soi
            INNER JOIN `tabSales Order` AS so ON soi.parent = so.name
            WHERE
                so.customer = %(customer)s AND
                so.docstatus = 1
            GROUP BY soi.item_group
        """,
        values={"customer": customer},
        as_dict=1,
    )

    def sum_group_by(field):
        def fn(label):
            filtered = filter(lambda x: x.item_group == label, items)
            return compose(sum, partial(pluck, field))(filtered)

        return fn

    return {
        "labels": labels,
        "datasets": [
            {"name": "Qty", "values": map(sum_group_by("qty"), labels)},
            {"name": "Amount", "values": map(sum_group_by("amount"), labels)},
        ],
    }
