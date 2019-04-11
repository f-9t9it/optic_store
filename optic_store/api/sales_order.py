# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from functools import partial
from toolz import pluck, unique, compose

from optic_store.api.customer import get_user_branch


@frappe.whitelist()
def invoice_qol(name, mode_of_payment=None, amount=None):
    doc = make_sales_invoice(name)
    if mode_of_payment and amount:
        doc.is_pos = 1
        doc.append("payments", {"mode_of_payment": mode_of_payment, "amount": amount})
    doc.insert(ignore_permissions=True)
    doc.submit()
    return {
        "sales_invoice_name": doc.name,
        "print_format": _get_print_format(),
        "no_letterhead": "0" if doc.letter_head else "0",
    }


def _get_print_format():
    return (
        frappe.db.get_single_value("Optical Settings", "default_print_format")
        or frappe.get_meta("Sales Invoice").default_print_format
        or "Standard"
    )


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
    return {
        "sales_invoice_name": make_unique(invoices),
        "print_format": _get_print_format(),
        "no_letterhead": "0",
    }


@frappe.whitelist()
def get_warehouse():
    branch = get_user_branch()
    return frappe.db.get_value("Branch", branch, "warehouse") if branch else None
