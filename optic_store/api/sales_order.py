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


workflow = {
    "name": "Optic Store Sales Order",
    "document_type": "Sales Order",
    "is_active": 1,
    "send_email_alert": 0,
    "workflow_state_field": "workflow_state",
    "states": [
        {
            "state": "Draft",
            "style": "Danger",
            "doc_status": "0",
            "allow_edit": "Sales User",
        },
        {
            "state": "Processing at Branch",
            "style": "Primary",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
        {
            "state": "Sent to HQM",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Store User",
        },
        {
            "state": "With Special Order Incharge",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Store User",
        },
        {
            "state": "Processing at HQM",
            "style": "Primary",
            "doc_status": "1",
            "allow_edit": "Lab Tech",
        },
        {
            "state": "Processing for Delivery",
            "style": "Info",
            "doc_status": "1",
            "allow_edit": "Store User",
        },
        {
            "state": "In Transit (with Driver)",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
        {
            "state": "Ready to Deliver",
            "style": "Success",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
    ],
    "transitions": [
        {
            "state": "Draft",
            "action": "Process at Branch",
            "next_state": "Processing at Branch",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "not doc.os_is_special_order and doc.os_is_branch_order",
        },
        {
            "state": "Processing at Branch",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
        {
            "state": "Draft",
            "action": "Send to HQM",
            "next_state": "Sent to HQM",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "not doc.os_is_special_order and not doc.os_is_branch_order",
        },
        {
            "state": "Sent to HQM",
            "action": "Process at HQM",
            "next_state": "Processing at HQM",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Draft",
            "action": "Send as Special Order",
            "next_state": "With Special Order Incharge",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_is_special_order",
        },
        {
            "state": "With Special Order Incharge",
            "action": "Process Special Order",
            "next_state": "Processing at HQM",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Processing at HQM",
            "action": "Proceed to Deliver",
            "next_state": "Processing for Delivery",
            "allowed": "Lab Tech",
            "allow_self_approval": 1,
        },
        {
            "state": "Processing for Delivery",
            "action": "Send to Branch",
            "next_state": "In Transit (with Driver)",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "In Transit (with Driver)",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
    ],
}
