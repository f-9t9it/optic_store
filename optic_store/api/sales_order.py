# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import cint
from frappe.model.workflow import get_workflow, apply_workflow
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from functools import partial
from toolz import compose, keyfilter, cons, identity

from optic_store.api.customer import get_user_branch


@frappe.whitelist()
def invoice_qol(name, payments, loyalty_card_no, loyalty_program, loyalty_points):
    def set_cost_center(item):
        if cost_center:
            item.cost_center = cost_center

    doc = make_sales_invoice(name)
    if doc.os_branch:
        cost_center = frappe.db.get_value("Branch", doc.os_branch, "os_cost_center")
        map(set_cost_center, doc.items)
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
def get_warehouse():
    branch = get_user_branch()
    return frappe.db.get_value("Branch", branch, "warehouse") if branch else None


@frappe.whitelist()
def get_workflow_states():
    workflow = get_workflow("Sales Order")
    states = partial(map, lambda x: x.state)
    return states(workflow.states)


@frappe.whitelist()
def get_next_workflow_actions(state):
    workflow = get_workflow("Sales Order")
    nexts = compose(
        partial(map, lambda x: x.action), partial(filter, lambda x: x.state == state)
    )
    return nexts(workflow.transitions)


@frappe.whitelist()
def get_sales_orders(company, state, branch=None, from_date=None, to_date=None):
    make_conditions = compose(
        " AND ".join,
        partial(cons, "os_branch = %(branch)s") if branch else identity,
        partial(cons, "transaction_date BETWEEN %(from_date)s AND %(to_date)s")
        if from_date and to_date
        else identity,
    )
    return frappe.db.sql(
        """
            SELECT name AS sales_order, workflow_state, os_lab_tech AS lab_tech
            FROM `tabSales Order`
            WHERE {conditions}
        """.format(
            conditions=make_conditions(
                ["company = %(company)s", "workflow_state = %(state)s"]
            )
        ),
        values={
            "company": company,
            "state": state,
            "branch": branch,
            "from_date": from_date,
            "to_date": to_date,
        },
        as_dict=1,
    )


@frappe.whitelist()
def update_sales_orders(sales_orders, action, lab_tech=None):
    transition = compose(
        lambda doc: apply_workflow(doc, action), partial(frappe.get_doc, "Sales Order")
    )
    map(transition, json.loads(sales_orders))
    if lab_tech and action == "Proceed to Deliver":
        update = compose(
            lambda x: frappe.db.set_value("Sales Order", x, "os_lab_tech", lab_tech)
        )
        map(update, json.loads(sales_orders))


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
            "state": "Process Pending",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
        {
            "state": "Processing at Branch",
            "style": "Primary",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
        {
            "state": "With Special Order Incharge",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Store User",
        },
        {
            "state": "Ordered to Supplier",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Store User",
        },
        {
            "state": "Sent to HQM",
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
            "allow_edit": "Store User",
        },
        {
            "state": "Ready to Deliver",
            "style": "Success",
            "doc_status": "1",
            "allow_edit": "Sales User",
        },
        {
            "state": "Cancelled",
            "style": "Danger",
            "doc_status": "2",
            "allow_edit": "Sales User",
        },
    ],
    "transitions": [
        {
            "state": "Draft",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_order_type == 'Eye Test'",
        },
        {
            "state": "Draft",
            "action": "Process at Branch",
            "next_state": "Process Pending",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_order_type == 'Sales' and doc.os_item_type == 'Other'",
        },
        {
            "state": "Process Pending",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
        {
            "state": "Process Pending",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
        {
            "state": "Draft",
            "action": "Process at Branch",
            "next_state": "Processing at Branch",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_order_type == 'Repair' or (doc.os_order_type == 'Sales' and doc.os_item_type == 'Standard')",  # noqa
        },
        {
            "state": "Processing at Branch",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
        {
            "state": "Processing at Branch",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
        {
            "state": "Draft",
            "action": "Send to HQM",
            "next_state": "Sent to HQM",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_order_type == 'Repair' or (doc.os_order_type == 'Sales' and doc.os_item_type == 'Standard')",  # noqa
        },
        {
            "state": "Sent to HQM",
            "action": "Process Order",
            "next_state": "Processing at HQM",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Sent to HQM",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Draft",
            "action": "Send as Special Order",
            "next_state": "With Special Order Incharge",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "doc.os_order_type == 'Sales' and doc.os_item_type == 'Special'",  # noqa
        },
        {
            "state": "With Special Order Incharge",
            "action": "Order to Supplier",
            "next_state": "Ordered to Supplier",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "With Special Order Incharge",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Ordered to Supplier",
            "action": "Process Order",
            "next_state": "Processing at HQM",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "Ordered to Supplier",
            "action": "Cancel",
            "next_state": "Cancelled",
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
            "state": "Processing at HQM",
            "action": "Cancel",
            "next_state": "Cancelled",
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
            "state": "Processing for Delivery",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "In Transit (with Driver)",
            "action": "Complete",
            "next_state": "Ready to Deliver",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "In Transit (with Driver)",
            "action": "Reject",
            "next_state": "Processing at HQM",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
        {
            "state": "In Transit (with Driver)",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Store User",
            "allow_self_approval": 1,
        },
    ],
}
