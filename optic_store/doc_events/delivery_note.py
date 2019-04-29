# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import compose, unique, pluck


def validate(doc, method):
    get_sales_orders = compose(
        list,
        unique,
        partial(filter, lambda x: x),
        partial(map, lambda x: x.against_sales_order),
    )
    sales_orders = get_sales_orders(doc.items)
    if sales_orders and not _are_billed(sales_orders):
        frappe.throw("Reference Sales Order not billed fully")
    if sales_orders and not _are_paid(sales_orders):
        frappe.throw("Sales Invoice not paid fully")


def _are_billed(sales_orders):
    statuses = map(
        partial(frappe.db.get_value, "Sales Order", fieldname="billing_status"),
        sales_orders,
    )
    return reduce(lambda a, x: a and (x in ["Fully Billed", "Closed"]), statuses, True)


def _are_paid(sales_orders):
    statuses = pluck(
        "status",
        frappe.db.sql(
            """
                SELECT si.status AS status
                FROM `tabSales Invoice Item` AS sii
                LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
                WHERE sii.sales_order IN %(sales_orders)s AND si.docstatus = 1
            """,
            values={"sales_orders": sales_orders},
            as_dict=1,
        ),
    )
    return reduce(lambda a, x: a and (x in ["Paid"]), statuses, True)
