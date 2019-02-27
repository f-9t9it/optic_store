# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice


@frappe.whitelist()
def invoice_qol(name, mode_of_payment=None, amount=None):
    doc = make_sales_invoice(name)
    if amount:
        doc.is_pos = 1
        doc.append("payments", {"mode_of_payment": mode_of_payment, "amount": amount})
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc
