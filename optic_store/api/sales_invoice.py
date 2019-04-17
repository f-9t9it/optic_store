# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note


@frappe.whitelist()
def deliver_qol(name):
    doc = make_delivery_note(name)
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc.name
