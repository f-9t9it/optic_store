# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import merge


@frappe.whitelist()
def setup_defaults():
    frappe.only_for("System Manager")
    _create_item_groups()
    _update_settings()
    _setup_workflow()


def _create_item_groups():
    def create_group(parent="All Item Groups", is_group=0):
        def fn(name, abbr=None):
            if not frappe.db.exists("Item Group", name):
                frappe.get_doc(
                    {
                        "doctype": "Item Group",
                        "item_group_name": name,
                        "item_group_abbr": abbr,
                        "parent_item_group": parent,
                        "is_group": is_group,
                    }
                ).insert(ignore_permissions=True)

        return fn

    def run_creator(name, value):
        create_group(is_group=1)(name)
        map(lambda x: create_group(parent=name)(*x), value.items())

    groups = {
        "Prescription": {
            "Frame": "FR",
            "Prescription Lens": None,
            "Special Order Prescription Lens": None,
            "Contact Lens": "CL",
            "Reader": None,
        },
        "Others": {"Sunglasses": "SG", "Accessories": "AC", "Solutions": "SL"},
    }

    map(lambda x: run_creator(*x), groups.items())


def _update_settings():
    def update(doctype, params):
        doc = frappe.get_single(doctype)
        map(lambda x: doc.set(*x), params.items())
        doc.save(ignore_permissions=True)

    settings = {
        "Selling Settings": {"cust_master_name": "Naming Series"},
        "Stock Settings": {"item_naming_by": "Naming Series", "show_barcode_field": 1},
    }

    map(lambda x: update(*x), settings.items())


def _setup_workflow():
    def make_action(name):
        if not frappe.db.exists("Workflow Action Master", name):
            frappe.get_doc(
                {"doctype": "Workflow Action Master", "workflow_action_name": name}
            ).insert(ignore_permissions=True)

    def make_state(name, style=None):
        if not frappe.db.exists("Workflow State", name):
            frappe.get_doc(
                {
                    "doctype": "Workflow State",
                    "workflow_state_name": name,
                    "style": style,
                }
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow State", name)
            doc.update({"style": style})
            doc.save(ignore_permissions=True)

    def make_role(name, desk_access=1):
        if not frappe.db.exists("Role", name):
            frappe.get_doc(
                {"doctype": "Role", "role_name": name, "desk_access": desk_access}
            ).insert(ignore_permissions=True)

    def make_workflow(name, **args):
        if args.get("transitions"):
            map(lambda x: make_action(x.get("action")), args.get("transitions"))
        if args.get("states"):
            map(
                lambda x: make_state(x.get("state"), x.get("style")), args.get("states")
            )
            map(lambda x: make_role(x.get("allow_edit")), args.get("states"))
        if not frappe.db.exists("Workflow", name):
            frappe.get_doc(
                merge({"doctype": "Workflow", "workflow_name": name}, args)
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow", name)
            doc.update(args)
            doc.save(ignore_permissions=True)

    map(
        lambda x: make_workflow(**x),
        [
            {
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
                    },
                    {
                        "state": "Processing at Branch",
                        "action": "Complete",
                        "next_state": "Ready to Deliver",
                        "allowed": "Sales User",
                    },
                    {
                        "state": "Draft",
                        "action": "Send to HQM",
                        "next_state": "Sent to HQM",
                        "allowed": "Sales User",
                    },
                    {
                        "state": "Sent to HQM",
                        "action": "Process at HQM",
                        "next_state": "Processing at HQM",
                        "allowed": "Store User",
                    },
                    {
                        "state": "Processing at HQM",
                        "action": "Proceed to Deliver",
                        "next_state": "Processing for Delivery",
                        "allowed": "Lab Tech",
                    },
                    {
                        "state": "Processing for Delivery",
                        "action": "Send to Branch",
                        "next_state": "In Transit (with Driver)",
                        "allowed": "Store User",
                    },
                    {
                        "state": "In Transit (with Driver)",
                        "action": "Complete",
                        "next_state": "Ready to Deliver",
                        "allowed": "Sales User",
                    },
                ],
            }
        ],
    )
