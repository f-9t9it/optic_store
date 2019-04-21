# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import cint
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from functools import partial
from toolz import pluck, unique, compose, keyfilter

from optic_store.api.customer import get_user_branch


@frappe.whitelist()
def invoice_qol(name, payments, loyalty_card_no, loyalty_program, loyalty_points):
    doc = make_sales_invoice(name)
    if loyalty_program and loyalty_points:
        doc.redeem_loyalty_points = 1
        doc.os_loyalty_card_no = loyalty_card_no
        doc.loyalty_program = loyalty_program
        doc.loyalty_points = cint(loyalty_points)
    if payments:
        doc.is_pos = 1
        add_payments = compose(
            partial(map, lambda x: doc.append("payments", x)),
            partial(
                map, partial(keyfilter, lambda x: x in ["mode_of_payment", "amount"])
            ),
            json.loads,
        )
        add_payments(payments)
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc.name


@frappe.whitelist()
def get_invoice(name):
    invoices = frappe.db.sql(
        """
            SELECT parent AS name FROM `tabSales Invoice Item`
            WHERE sales_order = %(sales_order)s
        """,
        values={"sales_order": name},
        as_dict=1,
    )
    make_unique = compose(unique, partial(pluck, "name"))
    return make_unique(invoices)


@frappe.whitelist()
def get_warehouse():
    branch = get_user_branch()
    return frappe.db.get_value("Branch", branch, "warehouse") if branch else None
