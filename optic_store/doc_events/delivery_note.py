# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.workflow import apply_workflow
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
        frappe.throw("Reference Sales Order not fully cleared or billed")
    if sales_orders and not _are_paid(sales_orders):
        frappe.throw("Cannot deliver until Sales Invoice is fully paid")


def _are_billed(sales_orders):
    def verify_status(field, values):
        statuses = map(
            partial(frappe.db.get_value, "Sales Order", fieldname=field), sales_orders
        )
        return reduce(lambda a, x: a and (x in values), statuses, True)

    return verify_status("billing_status", ["Fully Billed", "Closed"]) or verify_status(
        "status", ["To Deliver", "Closed"]
    )


def _are_paid(sales_orders):
    statuses = pluck(
        "status",
        frappe.db.sql(
            """
                SELECT si.status AS status
                FROM `tabSales Invoice Item` AS sii
                LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
                WHERE
                    sii.sales_order IN %(sales_orders)s AND
                    si.is_return = 0 AND
                    si.docstatus = 1
            """,
            values={"sales_orders": sales_orders},
            as_dict=1,
        ),
    )
    return reduce(lambda a, x: a and (x in ["Paid"]), statuses, True)


def on_submit(doc, method):
    def advance_wf(name):
        doc = frappe.get_doc("Sales Order", name)
        if doc and doc.workflow_state == "Ready to Deliver":
            apply_workflow(doc, "Complete")

    transit_sales_orders = compose(
        partial(map, advance_wf),
        unique,
        partial(filter, lambda x: x),
        partial(map, lambda x: x.against_sales_order),
    )

    transit_sales_orders(doc.items)
